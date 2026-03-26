const dbConnectionOptions = {
    minPoolSize: Number(process.env.MIN_POOL_SIZE),
    maxPoolSize: Number(process.env.MAX_POOL_SIZE),
    socketTimeoutMS: Number(process.env.SOCKET_TIMEOUT_MS),
};
export { dbConnectionOptions };