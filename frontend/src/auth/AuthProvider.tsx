import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { clearToken, getToken, setToken } from "../lib/storage";
import { login as loginApi, me as meApi, register as registerApi } from "../api/auth";
import type { AuthContextValue, LoginPayload, RegisterPayload, User } from "../types/auth";

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(getToken());
  const [loading, setLoading] = useState<boolean>(true);

  const refreshUser = useCallback(async () => {
    const currentToken = getToken();

    if (!currentToken) {
      setUser(null);
      setTokenState(null);
      setLoading(false);
      return;
    }

    try {
      const currentUser = await meApi();
      setUser(currentUser);
      setTokenState(currentToken);
    } catch {
      clearToken();
      setUser(null);
      setTokenState(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  const login = useCallback(async (payload: LoginPayload) => {
    const auth = await loginApi(payload);
    setToken(auth.access_token);
    setTokenState(auth.access_token);
    const currentUser = await meApi();
    setUser(currentUser);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    await registerApi(payload);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    setTokenState(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, token, loading, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}