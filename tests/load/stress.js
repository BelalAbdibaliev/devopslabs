import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 1000 }, 
    { duration: '5m', target: 1000 }, 
    { duration: '2m', target: 5000 }, 
    { duration: '5m', target: 5000 }, 
    { duration: '2m', target: 100 }, 
  ],
};

export default function () {
  const res = http.get('http://localhost:5000/api/orders');
  check(res, { 'status is 200': (r) => r.status === 200 });
}