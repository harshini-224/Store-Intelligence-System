import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    middlewareClientMaxBodySize: "500mb",
  },
  async rewrites() {
    // If INTERNAL_API_URL is set (Docker), use it. 
    // Otherwise fallback to localhost for local dev outside Docker.
    const apiUrl = process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";

    return {
      beforeFiles: [
        {
          source: "/health",
          destination: `${apiUrl}/health`,
        },
        {
          source: "/frontend-api/:path*",
          destination: `${apiUrl}/frontend-api/:path*`,
        },
        {
          source: "/ingest/:path*",
          destination: `${apiUrl}/ingest/:path*`,
        },
        {
          source: "/events/:path*",
          destination: `${apiUrl}/events/:path*`,
        },
        {
          source: "/metrics/:path*",
          destination: `${apiUrl}/metrics/:path*`,
        },
        {
          source: "/stores/:path*",
          destination: `${apiUrl}/stores/:path*`,
        },
        {
          source: "/recommendations/:path*",
          destination: `${apiUrl}/recommendations/:path*`,
        },
        {
          source: "/kpis/:path*",
          destination: `${apiUrl}/kpis/:path*`,
        },
        {
          source: "/anomalies/:path*",
          destination: `${apiUrl}/anomalies/:path*`,
        },
        {
          source: "/insights/:path*",
          destination: `${apiUrl}/insights/:path*`,
        },
      ],
      afterFiles: [],
      fallback: [],
    };
  },
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "127.0.0.1",
        port: "8000",
        pathname: "/**",
      },
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/**",
      },
      {
        protocol: "http",
        hostname: "api",
        port: "8000",
        pathname: "/**",
      },
    ],
  },
};

export default nextConfig;
