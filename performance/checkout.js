import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

const fixtures = new SharedArray('carts', function () {
  return JSON.parse(open('./fixtures/carts.json'));
});

export const options = {
  scenarios: {
    checkout: {
      executor: 'per-vu-iterations',
      vus: 10,
      iterations: 1,
      maxDuration: '2m',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{type:checkout}': ['p(95)<800'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

export function setup() {
  return fixtures.map((fixture) => {
    const login = http.post(
      `${BASE_URL}/auth/token`,
      JSON.stringify({ email: fixture.email, password: fixture.password }),
      { headers: { 'Content-Type': 'application/json' } },
    );
    return {
      cart_id: fixture.cart_id,
      access: login.json('access'),
    };
  });
}

export default function (data) {
  const fixture = data[__VU - 1];
  if (!fixture || !fixture.access) return;

  const checkout = http.post(
    `${BASE_URL}/orders`,
    JSON.stringify({ cart_id: fixture.cart_id }),
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${fixture.access}`,
        'Idempotency-Key': `checkout-${__VU}`,
      },
      tags: { type: 'checkout' },
    },
  );
  check(checkout, {
    'checkout is 201': (r) => r.status === 201,
    'order is pending': (r) => r.json('status') === 'PAYMENT_PENDING',
  });

  sleep(0.1);
}