const cookieOptions = {
    httpOnly: true,
    secure: true,
    // sameSite: process.env.NODE_ENV === "production" && "lax",
    maxAge: 24 * 60 * 60 * 1000,

    sameSite: process.env.NODE_ENV === "production" ? "none" : "lax",
    //   priority: 'high',
    // domain: ".onrender.com",
    path: "/",
};

export { cookieOptions };
