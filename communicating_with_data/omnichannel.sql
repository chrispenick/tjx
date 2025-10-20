create or replace TABLE TOUCHPOINTS (
	CUSTOMER_ID VARCHAR(50),
	TOUCHPOINT_SEQUENCE NUMBER(38,0),
	CHANNEL VARCHAR(50),
	ACTION_TYPE VARCHAR(50),
	PRODUCT_CATEGORY VARCHAR(50),
	DAYS_SINCE_FIRST_TOUCH NUMBER(38,0),
	SESSION_DURATION_MINUTES NUMBER(38,0),
	DEVICE_TYPE VARCHAR(50),
	LOCATION_TYPE VARCHAR(50),
	MARKETING_SOURCE VARCHAR(50),
	PRODUCT_VIEWS NUMBER(38,0),
	ITEMS_IN_CART NUMBER(38,0),
	CART_VALUE NUMBER(38,2),
	CONVERSION_FLAG BOOLEAN,
	TOUCHPOINT_TIMESTAMP VARCHAR(50),
	PAGE_DEPTH NUMBER(38,0),
	ASSISTED_BY_STAFF BOOLEAN,
	PERSONALIZATION_SHOWN BOOLEAN,
	INVENTORY_CHECKED BOOLEAN,
	PRICE_CHECKED BOOLEAN,
	REVIEWS_VIEWED BOOLEAN,
	COMPARISON_PRODUCTS NUMBER(38,0),
	PROMO_CODE_APPLIED BOOLEAN,
	LOYALTY_POINTS_EARNED NUMBER(38,0),
	CROSS_SELL_SHOWN BOOLEAN
);

create or replace TABLE OMNICHANNEL (
	CUSTOMER_ID VARCHAR(50),
	FIRST_TOUCH_CHANNEL VARCHAR(50),
	LAST_TOUCH_CHANNEL VARCHAR(50),
	JOURNEY_TYPE VARCHAR(50),
	TOTAL_TOUCHPOINTS NUMBER(38,0),
	DAYS_TO_PURCHASE NUMBER(38,0),
	PRODUCT_CATEGORY VARCHAR(50),
	ORDER_VALUE NUMBER(38,2),
	USED_MOBILE_APP BOOLEAN,
	USED_WEBSITE BOOLEAN,
	USED_STORE BOOLEAN,
	USED_SOCIAL BOOLEAN,
	USED_EMAIL BOOLEAN,
	USED_CALL_CENTER BOOLEAN,
	BOPIS_ORDER BOOLEAN,
	SHIP_FROM_STORE BOOLEAN,
	LOYALTY_MEMBER BOOLEAN,
	CUSTOMER_AGE NUMBER(38,0),
	LIFETIME_VALUE NUMBER(38,2),
	PURCHASE_COMPLETED BOOLEAN,
	CART_ABANDONMENT_STAGE VARCHAR(50),
	DEVICE_SWITCHES NUMBER(38,0),
	RESEARCH_TIME_HOURS NUMBER(38,1),
	IN_STORE_VISIT_COUNT NUMBER(38,0),
	EMAIL_OPENS NUMBER(38,0),
	SOCIAL_INTERACTIONS NUMBER(38,0),
	CUSTOMER_SATISFACTION_SCORE NUMBER(38,0),
	RETURN_FLAG BOOLEAN,
	CROSS_SELL_FLAG BOOLEAN,
	SEASON VARCHAR(50)
);

-- =====================================================
-- CHANNEL UTILIZATION ANALYSIS FOR OMNICHANNEL RETAIL
-- =====================================================

-- 1. INDIVIDUAL CHANNEL ADOPTION RATES
-- Shows what percentage of customers use each channel
WITH channel_adoption AS (
  SELECT 
    COUNT(*) as total_customers,
    SUM(CASE WHEN used_mobile_app THEN 1 ELSE 0 END) as mobile_app_users,
    SUM(CASE WHEN used_website THEN 1 ELSE 0 END) as website_users,
    SUM(CASE WHEN used_store THEN 1 ELSE 0 END) as store_users,
    SUM(CASE WHEN used_social THEN 1 ELSE 0 END) as social_users,
    SUM(CASE WHEN used_email THEN 1 ELSE 0 END) as email_users,
    SUM(CASE WHEN used_call_center THEN 1 ELSE 0 END) as call_center_users
  FROM OMNICHANNEL
)
SELECT 
  'Mobile App' as channel,
  mobile_app_users as users,
  ROUND(100.0 * mobile_app_users / total_customers, 2) as adoption_rate_pct
FROM channel_adoption
UNION ALL
SELECT 'Website', website_users, ROUND(100.0 * website_users / total_customers, 2)
FROM channel_adoption
UNION ALL
SELECT 'Store', store_users, ROUND(100.0 * store_users / total_customers, 2)
FROM channel_adoption
UNION ALL
SELECT 'Social', social_users, ROUND(100.0 * social_users / total_customers, 2)
FROM channel_adoption
UNION ALL
SELECT 'Email', email_users, ROUND(100.0 * email_users / total_customers, 2)
FROM channel_adoption
UNION ALL
SELECT 'Call Center', call_center_users, ROUND(100.0 * call_center_users / total_customers, 2)
FROM channel_adoption
ORDER BY adoption_rate_pct DESC;

-- 2. CHANNEL PARTICIPATION IN OMNICHANNEL JOURNEYS
-- Shows how often each channel appears in multi-channel customer journeys
WITH customer_channels AS (
  SELECT 
    customer_id,
    IFF(used_mobile_app, 1, 0) +
    IFF(used_website, 1, 0) +
    IFF(used_store, 1, 0) +
    IFF(used_social, 1, 0) +
    IFF(used_email, 1, 0) +
    IFF(used_call_center, 1, 0) as total_channels_used,
    used_mobile_app,
    used_website,
    used_store,
    used_social,
    used_email,
    used_call_center
  FROM OMNICHANNEL
),
omnichannel_customers AS (
  SELECT * FROM customer_channels WHERE total_channels_used >= 2
)
SELECT 
  'Mobile App' as channel,
  SUM(IFF(used_mobile_app, 1, 0)) as omni_appearances,
  COUNT(*) as total_omni_customers,
  ROUND(100.0 * SUM(IFF(used_mobile_app, 1, 0)) / COUNT(*), 2) as omni_participation_rate
FROM omnichannel_customers
UNION ALL
SELECT 
  'Website',
  SUM(IFF(used_website, 1, 0)),
  COUNT(*),
  ROUND(100.0 * SUM(IFF(used_website, 1, 0)) / COUNT(*), 2)
FROM omnichannel_customers
UNION ALL
SELECT 
  'Store',
  SUM(IFF(used_store, 1, 0)),
  COUNT(*),
  ROUND(100.0 * SUM(IFF(used_store, 1, 0)) / COUNT(*), 2)
FROM omnichannel_customers
UNION ALL
SELECT 
  'Social',
  SUM(IFF(used_social, 1, 0)),
  COUNT(*),
  ROUND(100.0 * SUM(IFF(used_social, 1, 0)) / COUNT(*), 2)
FROM omnichannel_customers
UNION ALL
SELECT 
  'Email',
  SUM(IFF(used_email, 1, 0)),
  COUNT(*),
  ROUND(100.0 * SUM(IFF(used_email, 1, 0)) / COUNT(*), 2)
FROM omnichannel_customers
UNION ALL
SELECT 
  'Call Center',
  SUM(IFF(used_call_center, 1, 0)),
  COUNT(*),
  ROUND(100.0 * SUM(IFF(used_call_center, 1, 0)) / COUNT(*), 2)
FROM omnichannel_customers
ORDER BY omni_participation_rate DESC;

-- 3. UNDERUTILIZATION SCORE
-- Combines metrics to identify most underutilized channels
WITH channel_metrics AS (
  SELECT 
    'Mobile App' as channel_name,
    SUM(IFF(used_mobile_app, 1, 0)) as total_users,
    COUNT(*) as total_customers,
    SUM(IFF(used_mobile_app AND 
        (IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + IFF(used_social, 1, 0) + 
         IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 1, 1, 0)) as omni_users,
    SUM(IFF((IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_social, 1, 0) + IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 2, 1, 0)) as total_omni_customers,
    SUM(IFF(used_mobile_app AND purchase_completed, 1, 0)) as converting_users,
    SUM(IFF(used_mobile_app AND loyalty_member, 1, 0)) as loyalty_users
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Website',
    SUM(IFF(used_website, 1, 0)),
    COUNT(*),
    SUM(IFF(used_website AND 
        (IFF(used_mobile_app, 1, 0) + IFF(used_store, 1, 0) + IFF(used_social, 1, 0) + 
         IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 1, 1, 0)),
    SUM(IFF((IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_social, 1, 0) + IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 2, 1, 0)),
    SUM(IFF(used_website AND purchase_completed, 1, 0)),
    SUM(IFF(used_website AND loyalty_member, 1, 0))
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Store',
    SUM(IFF(used_store, 1, 0)),
    COUNT(*),
    SUM(IFF(used_store AND 
        (IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_social, 1, 0) + 
         IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 1, 1, 0)),
    SUM(IFF((IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_social, 1, 0) + IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 2, 1, 0)),
    SUM(IFF(used_store AND purchase_completed, 1, 0)),
    SUM(IFF(used_store AND loyalty_member, 1, 0))
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Social',
    SUM(IFF(used_social, 1, 0)),
    COUNT(*),
    SUM(IFF(used_social AND 
        (IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 1, 1, 0)),
    SUM(IFF((IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_social, 1, 0) + IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 2, 1, 0)),
    SUM(IFF(used_social AND purchase_completed, 1, 0)),
    SUM(IFF(used_social AND loyalty_member, 1, 0))
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Email',
    SUM(IFF(used_email, 1, 0)),
    COUNT(*),
    SUM(IFF(used_email AND 
        (IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_social, 1, 0) + IFF(used_call_center, 1, 0)) >= 1, 1, 0)),
    SUM(IFF((IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_social, 1, 0) + IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 2, 1, 0)),
    SUM(IFF(used_email AND purchase_completed, 1, 0)),
    SUM(IFF(used_email AND loyalty_member, 1, 0))
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Call Center',
    SUM(IFF(used_call_center, 1, 0)),
    COUNT(*),
    SUM(IFF(used_call_center AND 
        (IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_social, 1, 0) + IFF(used_email, 1, 0)) >= 1, 1, 0)),
    SUM(IFF((IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + 
         IFF(used_social, 1, 0) + IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 2, 1, 0)),
    SUM(IFF(used_call_center AND purchase_completed, 1, 0)),
    SUM(IFF(used_call_center AND loyalty_member, 1, 0))
  FROM OMNICHANNEL
)
SELECT 
  channel_name,
  ROUND(100.0 * total_users / total_customers, 2) as adoption_rate,
  ROUND(100.0 * omni_users / NULLIF(total_omni_customers, 0), 2) as omni_participation_rate,
  ROUND(100.0 * converting_users / NULLIF(total_users, 0), 2) as conversion_rate,
  ROUND(100.0 * loyalty_users / NULLIF(total_users, 0), 2) as loyalty_correlation,
  -- Underutilization score (lower = more underutilized)
  ROUND((
    (100.0 * total_users / total_customers) * 0.3 +  -- Weight adoption
    (100.0 * omni_users / NULLIF(total_omni_customers, 0)) * 0.4 +  -- Weight omni participation  
    (100.0 * converting_users / NULLIF(total_users, 0)) * 0.3  -- Weight conversion
  ), 2) as utilization_score
FROM channel_metrics
ORDER BY utilization_score ASC;

-- 4. CHANNEL COMBINATION ANALYSIS
-- Shows which channel combinations are most/least common
-- This does not contain all the combinations
WITH channel_combos AS (
  SELECT 
    CASE 
      WHEN used_mobile_app AND used_website AND NOT used_store 
        AND NOT used_social AND NOT used_email AND NOT used_call_center 
        THEN 'Mobile App + Website'
      WHEN NOT used_mobile_app AND used_website AND used_store 
        AND NOT used_social AND NOT used_email AND NOT used_call_center 
        THEN 'Website + Store'
      WHEN used_mobile_app AND NOT used_website AND used_store 
        AND NOT used_social AND NOT used_email AND NOT used_call_center 
        THEN 'Mobile App + Store'
      WHEN NOT used_mobile_app AND used_website AND NOT used_store 
        AND used_social AND NOT used_email AND NOT used_call_center 
        THEN 'Website + Social'
      WHEN NOT used_mobile_app AND used_website AND NOT used_store 
        AND NOT used_social AND used_email AND NOT used_call_center 
        THEN 'Website + Email'
      WHEN used_website AND used_store AND used_email 
        AND NOT used_mobile_app AND NOT used_social AND NOT used_call_center
        THEN 'Website + Store + Email'
      WHEN used_mobile_app AND used_website AND used_store
        AND NOT used_social AND NOT used_email AND NOT used_call_center
        THEN 'Mobile App + Website + Store'
      ELSE 'Other/Multiple'
    END as channel_combination,
    COUNT(*) as customer_count,
    AVG(IFF(purchase_completed, 1.0, 0.0)) as conversion_rate,
    AVG(order_value) as avg_order_value,
    AVG(days_to_purchase) as avg_days_to_purchase
  FROM OMNICHANNEL
  WHERE (
    IFF(used_mobile_app, 1, 0) +
    IFF(used_website, 1, 0) +
    IFF(used_store, 1, 0) +
    IFF(used_social, 1, 0) +
    IFF(used_email, 1, 0) +
    IFF(used_call_center, 1, 0)
  ) >= 2
  GROUP BY channel_combination
)
SELECT 
  channel_combination,
  customer_count,
  ROUND(conversion_rate * 100, 2) as conversion_rate_pct,
  ROUND(avg_order_value, 2) as avg_order_value,
  ROUND(avg_days_to_purchase, 2) as avg_days_to_purchase
FROM channel_combos
ORDER BY customer_count DESC;

-- 5. TOUCHPOINT ENGAGEMENT BY CHANNEL
-- Analyzes engagement metrics from touchpoint data
WITH touchpoint_metrics AS (
  SELECT 
    channel,
    COUNT(*) as total_touchpoints,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(session_duration_minutes) as avg_session_duration,
    AVG(page_depth) as avg_page_depth,
    AVG(product_views) as avg_product_views,
    SUM(IFF(conversion_flag, 1, 0)) as conversions,
    AVG(cart_value) as avg_cart_value,
    SUM(IFF(personalization_shown, 1, 0)) as personalized_experiences,
    SUM(IFF(assisted_by_staff, 1, 0)) as staff_assisted,
    AVG(comparison_products) as avg_comparison_products
  FROM TOUCHPOINTS
  GROUP BY channel
)
SELECT 
  channel,
  total_touchpoints,
  unique_customers,
  ROUND(total_touchpoints::FLOAT / unique_customers, 2) as avg_touchpoints_per_customer,
  ROUND(avg_session_duration, 2) as avg_session_duration,
  ROUND(avg_page_depth, 2) as avg_page_depth,
  ROUND(avg_product_views, 2) as avg_product_views,
  ROUND(100.0 * conversions / total_touchpoints, 2) as conversion_rate,
  ROUND(avg_cart_value, 2) as avg_cart_value,
  ROUND(100.0 * personalized_experiences / total_touchpoints, 2) as personalization_rate,
  ROUND(100.0 * staff_assisted / total_touchpoints, 2) as staff_assistance_rate
FROM touchpoint_metrics
ORDER BY conversion_rate DESC;

-- 6. CHANNEL ABANDONMENT ANALYSIS
-- Identifies channels with high abandonment rates
SELECT 
  first_touch_channel,
  COUNT(*) as total_journeys,
  SUM(IFF(purchase_completed, 1, 0)) as completed_purchases,
  SUM(IFF(NOT purchase_completed, 1, 0)) as abandoned_journeys,
  ROUND(100.0 * SUM(IFF(NOT purchase_completed, 1, 0)) / COUNT(*), 2) as abandonment_rate,
  AVG(CASE WHEN NOT purchase_completed THEN days_to_purchase ELSE NULL END) as avg_days_before_abandonment,
  -- Distribution of abandonment stages
  SUM(CASE WHEN cart_abandonment_stage = 'browsing' THEN 1 ELSE 0 END) as abandoned_at_browsing,
  SUM(CASE WHEN cart_abandonment_stage = 'cart' THEN 1 ELSE 0 END) as abandoned_at_cart,
  SUM(CASE WHEN cart_abandonment_stage = 'checkout' THEN 1 ELSE 0 END) as abandoned_at_checkout,
  -- Additional metrics
  AVG(device_switches) as avg_device_switches,
  AVG(research_time_hours) as avg_research_hours
FROM OMNICHANNEL
GROUP BY first_touch_channel
ORDER BY abandonment_rate DESC;

-- 7. UNDERUTILIZATION SUMMARY
-- Final summary highlighting the most underutilized channels
WITH utilization_summary AS (
  SELECT 
    'Mobile App' as channel,
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_mobile_app) as users,
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_mobile_app 
     AND (IFF(used_website, 1, 0) + IFF(used_store, 1, 0) + IFF(used_social, 1, 0) +
          IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 1) as connects_to_other_channels,
    (SELECT AVG(order_value) FROM OMNICHANNEL WHERE used_mobile_app AND purchase_completed) as avg_order_value
  UNION ALL
  SELECT 
    'Website',
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_website),
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_website 
     AND (IFF(used_mobile_app, 1, 0) + IFF(used_store, 1, 0) + IFF(used_social, 1, 0) +
          IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 1),
    (SELECT AVG(order_value) FROM OMNICHANNEL WHERE used_website AND purchase_completed)
  UNION ALL
  SELECT 
    'Store',
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_store),
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_store 
     AND (IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_social, 1, 0) +
          IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 1),
    (SELECT AVG(order_value) FROM OMNICHANNEL WHERE used_store AND purchase_completed)
  UNION ALL
  SELECT 
    'Social',
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_social),
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_social 
     AND (IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) +
          IFF(used_email, 1, 0) + IFF(used_call_center, 1, 0)) >= 1),
    (SELECT AVG(order_value) FROM OMNICHANNEL WHERE used_social AND purchase_completed)
  UNION ALL
  SELECT 
    'Email',
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_email),
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_email 
     AND (IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) +
          IFF(used_social, 1, 0) + IFF(used_call_center, 1, 0)) >= 1),
    (SELECT AVG(order_value) FROM OMNICHANNEL WHERE used_email AND purchase_completed)
  UNION ALL
  SELECT 
    'Call Center',
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_call_center),
    (SELECT COUNT(*) FROM OMNICHANNEL WHERE used_call_center 
     AND (IFF(used_mobile_app, 1, 0) + IFF(used_website, 1, 0) + IFF(used_store, 1, 0) +
          IFF(used_social, 1, 0) + IFF(used_email, 1, 0)) >= 1),
    (SELECT AVG(order_value) FROM OMNICHANNEL WHERE used_call_center AND purchase_completed)
)
SELECT 
  channel,
  users as total_users,
  connects_to_other_channels,
  ROUND(100.0 * connects_to_other_channels / NULLIF(users, 0), 2) as cross_channel_rate,
  ROUND(avg_order_value, 2) as avg_order_value,
  CASE 
    WHEN users < 20 THEN 'Severely Underutilized'
    WHEN users < 40 AND (100.0 * connects_to_other_channels / NULLIF(users, 0)) < 50 
      THEN 'Underutilized - Low Cross-Channel'
    WHEN users < 40 THEN 'Underutilized - Low Adoption'
    ELSE 'Adequately Utilized'
  END as utilization_status
FROM utilization_summary
ORDER BY users ASC;

-- 8. MISSING CHANNEL CONNECTIONS ANALYSIS
-- Identifies which channel pairs are rarely connected
WITH channel_pairs AS (
  SELECT 
    'Mobile App → Website' as connection,
    SUM(IFF(used_mobile_app AND used_website, 1, 0)) as connections,
    SUM(IFF(used_mobile_app, 1, 0)) as source_users,
    ROUND(100.0 * SUM(IFF(used_mobile_app AND used_website, 1, 0)) / NULLIF(SUM(IFF(used_mobile_app, 1, 0)), 0), 2) as connection_rate
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Mobile App → Store',
    SUM(IFF(used_mobile_app AND used_store, 1, 0)),
    SUM(IFF(used_mobile_app, 1, 0)),
    ROUND(100.0 * SUM(IFF(used_mobile_app AND used_store, 1, 0)) / NULLIF(SUM(IFF(used_mobile_app, 1, 0)), 0), 2)
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Website → Store',
    SUM(IFF(used_website AND used_store, 1, 0)),
    SUM(IFF(used_website, 1, 0)),
    ROUND(100.0 * SUM(IFF(used_website AND used_store, 1, 0)) / NULLIF(SUM(IFF(used_website, 1, 0)), 0), 2)
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Social → Website',
    SUM(IFF(used_social AND used_website, 1, 0)),
    SUM(IFF(used_social, 1, 0)),
    ROUND(100.0 * SUM(IFF(used_social AND used_website, 1, 0)) / NULLIF(SUM(IFF(used_social, 1, 0)), 0), 2)
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Social → Store',
    SUM(IFF(used_social AND used_store, 1, 0)),
    SUM(IFF(used_social, 1, 0)),
    ROUND(100.0 * SUM(IFF(used_social AND used_store, 1, 0)) / NULLIF(SUM(IFF(used_social, 1, 0)), 0), 2)
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Email → Website',
    SUM(IFF(used_email AND used_website, 1, 0)),
    SUM(IFF(used_email, 1, 0)),
    ROUND(100.0 * SUM(IFF(used_email AND used_website, 1, 0)) / NULLIF(SUM(IFF(used_email, 1, 0)), 0), 2)
  FROM OMNICHANNEL
  UNION ALL
  SELECT 
    'Email → Store',
    SUM(IFF(used_email AND used_store, 1, 0)),
    SUM(IFF(used_email, 1, 0)),
    ROUND(100.0 * SUM(IFF(used_email AND used_store, 1, 0)) / NULLIF(SUM(IFF(used_email, 1, 0)), 0), 2)
  FROM OMNICHANNEL
)
SELECT 
  connection,
  connections,
  source_users,
  connection_rate,
  CASE 
    WHEN connection_rate < 20 THEN 'Critical Gap'
    WHEN connection_rate < 40 THEN 'Weak Connection'
    WHEN connection_rate < 60 THEN 'Moderate Connection'
    ELSE 'Strong Connection'
  END as connection_strength
FROM channel_pairs
ORDER BY connection_rate ASC;