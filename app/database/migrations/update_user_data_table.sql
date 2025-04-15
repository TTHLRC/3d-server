-- 删除旧的列
ALTER TABLE user_data
DROP COLUMN initial_content,
DROP COLUMN target_content,
DROP COLUMN real_time_content;

-- 添加新的 JSON 列
ALTER TABLE user_data
ADD COLUMN cube_data JSON; 