class CachedAnalysis(Base):
    __tablename__ = 'analysis_cache'
    
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String(100), nullable=False, index=True)
    chain = Column(String(10), nullable=False)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    
    __table_args__ = (UniqueConstraint('wallet_address', 'chain', name='_wallet_chain_uc'),)
