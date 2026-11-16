import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '60s', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{type:catalog}': ['p(95)<300'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

export default function () {
  const list = http.get(`${BASE_URL}/products?page=1`, { tags: { type: 'catalog' } });
  check(list, {
    'catalog list is 200': (r) => r.status === 200,
  });

  const detailId = __ENV.PRODUCT_ID;
  if (detailId) {
    const detail = http.get(`${BASE_URL}/products/${detailId}`, { tags: { type: 'catalog' } });
    check(detail, {
      'product detail is 200': (r) => r.status === 200,
    });
  }

  sleep(1);
}