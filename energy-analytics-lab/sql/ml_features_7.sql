-- Підготовка даних для прогнозу на 7 днів наперед
DROP TABLE IF EXISTS gas_prices_ml_7d;
CREATE TABLE gas_prices_ml_7d AS
SELECT
    observation_date,
    -- Майбутня ціна через 7 днів (наша ціль)
    LEAD(price_cleaned, 7) OVER (ORDER BY observation_date) as target_7d,

    -- Ознаки для навчання
    price_cleaned as current_price,
    LAG(price_cleaned, 1) OVER (ORDER BY observation_date) as lag_1,
    LAG(price_cleaned, 7) OVER (ORDER BY observation_date) as lag_7,
    moving_avg_30,
    strftime('%m', observation_date) as month_num
FROM gas_prices_metrics;

-- Видаляємо порожні рядки в кінці (де майбутнє ще не настало)
DELETE FROM gas_prices_ml_7d WHERE target_7d IS NULL;
