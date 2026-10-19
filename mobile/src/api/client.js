/**
 * API Client for CyberSafe Backend
 */

import axios from 'axios';
import {API_URL} from '../config';

const client = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Check connection to backend
export const checkConnection = async () => {
  try {
    const response = await client.get('/api/status');
    return response.data;
  } catch (error) {
    throw new Error('Cannot connect to backend');
  }
};

// Get system status
export const getStatus = async () => {
  const response = await client.get('/api/status');
  return response.data;
};

// Start monitoring
export const startMonitoring = async (interface_name = null) => {
  const response = await client.post('/api/start', {
    interface: interface_name,
  });
  return response.data;
};

// Stop monitoring
export const stopMonitoring = async () => {
  const response = await client.post('/api/stop');
  return response.data;
};

// Get packets
export const getPackets = async (count = 100) => {
  const response = await client.get(`/api/packets?count=${count}`);
  return response.data;
};

// Get threats
export const getThreats = async (count = 100, type = null) => {
  let url = `/api/threats?count=${count}`;
  if (type) {
    url += `&type=${type}`;
  }
  const response = await client.get(url);
  return response.data;
};

// Get ports
export const getPorts = async () => {
  const response = await client.get('/api/ports');
  return response.data;
};

// Get statistics
export const getStats = async () => {
  const response = await client.get('/api/stats');
  return response.data;
};

// Get protocols
export const getProtocols = async () => {
  const response = await client.get('/api/protocols');
  return response.data;
};

// Get available interfaces
export const getInterfaces = async () => {
  const response = await client.get('/api/interfaces');
  return response.data;
};

// Reset statistics
export const resetStats = async () => {
  const response = await client.post('/api/reset');
  return response.data;
};

export default client;
