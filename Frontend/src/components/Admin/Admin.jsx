import { useState } from "react";
import AdminsList from "./AdminsList";
import InvigilatorsList from "./InvigilatorsList";
import AdminExams from "./AdminExams";
import Layout from "../Layout/Layout";
import Button from "../ui/Button";
import { Shield, Users, FileText } from "lucide-react";

const Admin = () => {
    const [activeTab, setActiveTab] = useState("admins");

    return (
        <Layout title="Admin Management">
            <div className="space-y-6">
                {/* Tabs */}
                <div className="flex gap-2 border-b border-neutral-200">
                    <button
                        onClick={() => setActiveTab("admins")}
                        className={`px-4 py-2 text-sm font-medium transition-colors ${
                            activeTab === "admins"
                                ? "text-accent border-b-2 border-accent"
                                : "text-neutral-600 hover:text-neutral-900"
                        }`}
                    >
                        <div className="flex items-center gap-2">
                            <Shield className="w-4 h-4" />
                            Admins
                        </div>
                    </button>
                    <button
                        onClick={() => setActiveTab("invigilators")}
                        className={`px-4 py-2 text-sm font-medium transition-colors ${
                            activeTab === "invigilators"
                                ? "text-accent border-b-2 border-accent"
                                : "text-neutral-600 hover:text-neutral-900"
                        }`}
                    >
                        <div className="flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            Invigilators
                        </div>
                    </button>
                    <button
                        onClick={() => setActiveTab("exams")}
                        className={`px-4 py-2 text-sm font-medium transition-colors ${
                            activeTab === "exams"
                                ? "text-accent border-b-2 border-accent"
                                : "text-neutral-600 hover:text-neutral-900"
                        }`}
                    >
                        <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4" />
                            Exams
                        </div>
                    </button>
                </div>

                {/* Content */}
                {activeTab === "admins" && <AdminsList />}
                {activeTab === "invigilators" && <InvigilatorsList />}
                {activeTab === "exams" && <AdminExams />}
            </div>
        </Layout>
    );
};

export default Admin;
