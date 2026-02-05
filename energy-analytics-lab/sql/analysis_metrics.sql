-- Розрахунок 30-денного ковзного середнього
DROP TABLE IF EXISTS gas_prices_metrics;
CREATE TABLE gas_prices_metrics AS
SELECT
    observation_date,
    price_cleaned,
    -- Рахуємо середнє значення за поточний день + 29 попередніх
    AVG(price_cleaned) OVER (
        ORDER BY observation_date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as moving_avg_30
FROM gas_prices_final;

-- Перевірка перших результатів
SELECT * FROM gas_prices_metrics WHERE moving_avg_30 IS NOT NULL LIMIT 10;
