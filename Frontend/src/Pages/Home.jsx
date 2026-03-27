import React, { useState, useEffect } from "react";
import { InvigilatorApi } from "../Api/Invigilator/Invigilator.Api.js";
const Home = () => {
    const [invigilator, setInvigilator] = useState(null);
    const invigilatorApi = new InvigilatorApi();

    useEffect(() => {
        (async () => {
            try {
                const data = await invigilatorApi.getAllInvigilators();
                console.log("Invigilator data:", data);
                setInvigilator(data);
            } catch (error) {
                console.error("Error fetching invigilator data:", error);
            }
        })();
    }, []);
    return (
        <div className="home">
            <h1>Welcome to the Invigilator Dashboard</h1>
            <p>
                Here you can manage your exams, monitor students, and review
                reports.
            </p>
            {invigilator && Array.isArray(invigilator) ? (
                <div>
                    <h2>Invigilator Information:</h2>
                    {invigilator.map((inv) => (
                        <div key={inv.id}>
                            <p>Name: {inv.name}</p>
                            <p>Email: {inv.email}</p>
                        </div>
                    ))}
                </div>
            ) : null}
        </div>
    );
};

export default Home;
