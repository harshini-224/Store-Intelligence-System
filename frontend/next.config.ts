import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    middlewareClientMaxBodySize: "500mb",
  },
  async rewrites() {
    const apiUrl = process.env.INTERNAL_API_URL || "http://api:8000";

    return {
      beforeFiles: [
        {
          source: "/frontend-api/health",
          destination: `${apiUrl}/health`,
        },
        {
          source: "/ingest/:path*",
          destination: `${apiUrl}/ingest/:path*`,
        },
        {
          source: "/frontend-api/:path*",
          destination: `${apiUrl}/frontend-api/:path*`,
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
          source: "/recommendations/:path*",
          destination: `${apiUrl}/recommendations/:path*`,
        },
        {
          source: "/kpis/:path*",
          destination: `${apiUrl}/kpis/:path*`,
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
    ],
  },
};

export default nextConfig;
