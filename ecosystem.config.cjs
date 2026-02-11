/**
 * PM2 生態檔 - Mock Exam Tutor
 * 使用方式：
 *   pm2 start ecosystem.config.cjs
 *   pm2 stop all
 *   pm2 restart all
 *   pm2 logs
 */

module.exports = {
  apps: [
    {
      name: 'mock-exam-backend',
      cwd: './backend',
      script: 'venv/bin/python',
      args: '-m uvicorn main:app --host 0.0.0.0 --port 8000',
      interpreter: 'none',
      env: { NODE_ENV: 'development' },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '2s',
    },
    {
      name: 'mock-exam-frontend',
      cwd: './frontend',
      script: 'npm',
      args: ['run', 'dev'],
      interpreter: 'none',
      env: { NODE_ENV: 'development', PORT: 3000 },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '2s',
    },
  ],
};
