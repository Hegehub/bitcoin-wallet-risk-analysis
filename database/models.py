class CachedAnalysis(Base):
    __tablename__ = 'analysis_cache'
    
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String(100), nullable=False, index=True)
    chain = Column(String(10), nullable=False)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    
    __table_args__ = (UniqueConstraint('wallet_address', 'chain', name='_wallet_chain_uc'),)

async def get_cached_analysis(address: str, chain: str) -> Optional[Dict]:
    async with async_session() as session:
        result = await session.execute(
            select(CachedAnalysis).where(
                CachedAnalysis.wallet_address == address,
                CachedAnalysis.chain == chain,
                CachedAnalysis.expires_at > datetime.now()
            )
        )
        cached = result.scalar_one_or_none()
        if cached:
            return cached.result_json
    return None

async def save_cached_analysis(address: str, chain: str, result: Dict, ttl_days: int):
    async with async_session() as session:
        expires_at = datetime.now() + timedelta(days=ttl_days)
        # upsert
        await session.execute(
            CachedAnalysis.__table__.insert().on_conflict_do_update(
                index_elements=['wallet_address', 'chain'],
                set_={
                    'result_json': result,
                    'created_at': datetime.now(),
                    'expires_at': expires_at
                }
            ),
            dict(wallet_address=address, chain=chain, result_json=result, expires_at=expires_at)
        )
        await session.commit()
