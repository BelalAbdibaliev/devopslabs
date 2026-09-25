import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    vus: 100, duration: '5m'
};

export default function () {
    const res = http.post('http://localhost:5000/api/orders'); // Hits Gateway
    sleep(1);
}