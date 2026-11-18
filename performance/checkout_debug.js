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
      vus: 1,
      iterations: 1,
      maxDuration: '2m',
    },
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000/api/v1';

export default function () {
  const fixture = fixtures[__VU - 1];

  const login = http.post(
    `${BASE_URL}/auth/token`,
    JSON.stringify({ email: fixture.email, password: fixture.password }),
    { headers: { 'Content-Type': 'application/json' } },
  );
  console.log('LOGIN', login.status, login.body);
  const accessToken = login.json('access');

  const checkout = http.post(
    `${BASE_URL}/orders`,
    JSON.stringify({ cart_id: fixture.cart_id }),
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'Idempotency-Key': `checkout-${__VU}`,
      },
    },
  );
  console.log('CHECKOUT', checkout.status, checkout.body);

  sleep(0.1);
}