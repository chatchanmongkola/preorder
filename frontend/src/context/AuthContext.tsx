import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useMemo,
    useState,
    type ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import liff from "@line/liff";

import { getMe, liffLogin } from "../api/auth";
import { TOKEN_STORAGE_KEY } from "../api/client";
import type { User } from "../api/types";

interface AuthContextValue {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    setToken: (token: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [token, setTokenState] = useState<string | null>(() =>
        localStorage.getItem(TOKEN_STORAGE_KEY),
    );
    const queryClient = useQueryClient();

    // true while LIFF is initialising — keeps RequireAuth in a loading state so
    // it does not redirect to /login before the LINE OAuth callback is processed.
    const [liffIniting, setLiffIniting] = useState(
        () =>
            !!import.meta.env.VITE_LIFF_ID &&
            !localStorage.getItem(TOKEN_STORAGE_KEY),
    );

    // Handle LIFF redirect-back: must run before any routing decision
    useEffect(() => {
        const liffId = import.meta.env.VITE_LIFF_ID as string | undefined;
        if (!liffId || localStorage.getItem(TOKEN_STORAGE_KEY)) {
            setLiffIniting(false);
            return;
        }

        liff.init({ liffId })
            .then(() => {
                if (!liff.isLoggedIn()) return;
                const idToken = liff.getIDToken();
                if (!idToken) return;
                return liffLogin(idToken).then((newToken) => {
                    localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
                    setTokenState(newToken);
                });
            })
            .catch(() => {
                // init failed or token exchange failed — let user retry on /login
            })
            .finally(() => setLiffIniting(false));
    }, []); // intentionally run once on mount

    const { data: user, isLoading } = useQuery({
        queryKey: ["auth", "me", token],
        queryFn: getMe,
        enabled: !!token,
        retry: false,
    });

    const setToken = useCallback((newToken: string) => {
        localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
        setTokenState(newToken);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setTokenState(null);
        queryClient.clear();
    }, [queryClient]);

    useEffect(() => {
        // keep other tabs in sync
        const onStorage = (e: StorageEvent) => {
            if (e.key === TOKEN_STORAGE_KEY) setTokenState(e.newValue);
        };
        window.addEventListener("storage", onStorage);
        return () => window.removeEventListener("storage", onStorage);
    }, []);

    const value = useMemo<AuthContextValue>(
        () => ({
            user: user ?? null,
            isLoading: liffIniting || (!!token && isLoading),
            isAuthenticated: !!token && !!user,
            setToken,
            logout,
        }),
        [user, isLoading, token, liffIniting, setToken, logout],
    );

    return (
        <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within AuthProvider");
    return ctx;
}
