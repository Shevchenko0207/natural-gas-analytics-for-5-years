DROP TABLE IF EXISTS gas_prices_cleaned;
CREATE TABLE gas_prices_cleaned AS
SELECT
    observation_date,
    CASE
        -- 1. Обробка пропусків та нулів (те, що ми вже зробили)
        WHEN price_usd = '.' OR price_usd = '0' OR price_usd = '0.0' OR price_usd = '' THEN NULL

        -- 2. Обробка аномальних стрибків (Outliers)
        -- Якщо ціна вище 20, ми її "підрізаємо", щоб вона не ламала статистику
        WHEN CAST(price_usd AS NUMERIC) > 20 THEN 20.0

        ELSE CAST(price_usd AS NUMERIC)
    END as price_cleaned
FROM gas_prices_raw;
