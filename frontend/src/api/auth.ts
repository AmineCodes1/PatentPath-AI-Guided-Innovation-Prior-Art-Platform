/**
 * Typed auth API helpers for register, login, profile, and token refresh.
 */

import apiClient from "./client";
import type { LoginPayload, RegisterPayload, TokenResponse, User } from "../types/auth";

export async function register(data: RegisterPayload): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/register", data);
  return response.data;
}

export async function login(data: LoginPayload): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/login", data);
  return response.data;
}

export async function getMe(): Promise<User> {
  const response = await apiClient.get<User>("/auth/me");
  return response.data;
}

export async function refreshToken(): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/refresh");
  return response.data;
}
