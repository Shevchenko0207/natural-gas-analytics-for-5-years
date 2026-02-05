CREATE TABLE IF NOT EXISTS gas_prices_raw (
    observation_date DATE PRIMARY KEY,
    price_usd NUMERIC
);

-- Команда для перевірки завантаження
SELECT * FROM gas_prices_raw LIMIT 5;

