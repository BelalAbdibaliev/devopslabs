import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    stages: [{ duration: '1m', target: 50 }, { duration: '2m', target: 200 }, { duration: '2m', target: 500 }, { duration: '1m', target: 0 }]
};

export default function () {
    const res = http.post('http://localhost:5000/api/orders'); // Hits Gateway
    sleep(1);
}