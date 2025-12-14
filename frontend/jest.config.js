/** @type {import('jest').Config} */
module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/src/test-setup.ts'],
  globalSetup: 'jest-preset-angular/global-setup',
  testMatch: [
    '<rootDir>/**/*.spec.[jt]s?(x)'
  ],
  coverageDirectory: 'coverage',
};