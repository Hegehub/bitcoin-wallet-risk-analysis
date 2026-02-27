pybabel extract -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ru
pybabel compile -d locales
