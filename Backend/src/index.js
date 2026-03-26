import { app } from "./app.js";
import { connectDB } from "./db/db.js";

app.listen(process.env.PORT, () => {
    connectDB().then(() => {
        console.log(`Server is running on port ${process.env.PORT}`);
    });
});
