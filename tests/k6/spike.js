import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    stages: [{ duration: '10s', target: 100 }, { duration: '10s', target: 2000 }, { duration: '3m', target: 2000 }, { duration: '10s', target: 100 }]
};

export default function () {
    const res = http.post('http://localhost:5000/api/orders'); // Hits Gateway
    sleep(1);
}