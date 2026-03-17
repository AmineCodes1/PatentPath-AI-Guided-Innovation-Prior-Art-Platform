/**
 * Shared authentication-related frontend types.
 */

export type User = {
  id: string;
  email: string;
  display_name: string;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  display_name: string;
};
