const cookieOptions = {
    httpOnly: true,
    secure: true,
    maxAge: 24 * 60 * 60 * 1000,
    sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
};

export { cookieOptions };
