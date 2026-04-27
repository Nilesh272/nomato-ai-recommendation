import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Prevent Next from inferring an incorrect workspace root due to lockfiles
  // elsewhere on the machine.
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;
