-- Підготовка набору даних для Machine Learning
DROP TABLE IF EXISTS gas_prices_ml;
CREATE TABLE gas_prices_ml AS
SELECT
    observation_date,
    price_cleaned as target_price, -- Те, що ми будемо прогнозувати

    -- Лаги (ціни в минулому)
    LAG(price_cleaned, 1) OVER (ORDER BY observation_date) as lag_1,
    LAG(price_cleaned, 7) OVER (ORDER BY observation_date) as lag_7,

    -- Метрика тренду, яку ми вже рахували
    moving_avg_30,

    -- Витягуємо місяць для врахування сезонності
    strftime('%m', observation_date) as month_num
FROM gas_prices_metrics;

-- Видаляємо перші 30 рядків, де ще немає ковзного середнього
DELETE FROM gas_prices_ml WHERE moving_avg_30 IS NULL;
