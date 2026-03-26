const dbConnectionOptions = {
    minPoolSize: process.env.MIN_POOL_SIZE,
    maxPoolSize: process.env.MAX_POOL_SIZE,
    socketTimeoutMS: process.env.SOCKET_TIMEOUT_MS,
};
export { dbConnectionOptions };