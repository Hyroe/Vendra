import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 5 },
    { duration: '60s', target: 20 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{type:checkout}': ['p(95)<800'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

export default function () {
  // Checkout load testing requires pre-created users, carts and inventory.
  // This script is a template and must be adapted to the test fixture setup.
  const response = http.get(`${BASE_URL}/healthz`, { tags: { type: 'checkout' } });
  check(response, {
    'health endpoint is 200': (r) => r.status === 200,
  });

  sleep(1);
}