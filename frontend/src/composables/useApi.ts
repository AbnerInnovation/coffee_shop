import { inject } from 'vue';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: any;
  config: AxiosRequestConfig;
}

export function useApi() {
  const api = inject<AxiosInstance>('axios');
  
  if (!api) {
    throw new Error('Axios instance not provided. Make sure to provide axios instance with provide("axios", axiosInstance)');
  }

  const handleApiError = (error: any) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error Response:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
      });
    } else if (error.request) {
      // The request was made but no response was received
      console.error('API Error Request:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('API Error:', error.message);
    }
  };

  const get = async <T = any>(
    url: string, 
    config: AxiosRequestConfig = {}
  ): Promise<T> => {
    try {
      const response: AxiosResponse<T> = await api.get<T>(url, config);
      return response.data;
    } catch (error: any) {
      handleApiError(error);
      throw error;
    }
  };

  const post = async <T = any>(
    url: string, 
    data: any = {}, 
    config: AxiosRequestConfig = {}
  ): Promise<T> => {
    try {
      const response: AxiosResponse<T> = await api.post<T>(url, data, config);
      return response.data;
    } catch (error: any) {
      handleApiError(error);
      throw error;
    }
  };

  const put = async <T = any>(
    url: string, 
    data: any = {}, 
    config: AxiosRequestConfig = {}
  ): Promise<T> => {
    try {
      const response: AxiosResponse<T> = await api.put<T>(url, data, config);
      return response.data;
    } catch (error: any) {
      handleApiError(error);
      throw error;
    }
  };

  const patch = async <T = any>(
    url: string, 
    data: any = {}, 
    config: AxiosRequestConfig = {}
  ): Promise<T> => {
    try {
      const response: AxiosResponse<T> = await api.patch<T>(url, data, config);
      return response.data;
    } catch (error: any) {
      handleApiError(error);
      throw error;
    }
  };

  const del = async <T = any>(
    url: string, 
    config: AxiosRequestConfig = {}
  ): Promise<T> => {
    try {
      const response: AxiosResponse<T> = await api.delete<T>(url, config);
      return response.data;
    } catch (error: any) {
      handleApiError(error);
      throw error;
    }
  };

  return {
    api,
    get,
    post,
    put,
    patch,
    delete: del,
  };
}

export default useApi;
