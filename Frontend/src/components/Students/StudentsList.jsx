import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import studentApis from "../../apis/Students/student.apis.js";
import { Link } from "react-router-dom";

export default function StudentsList() {
    const [page, setPage] = useState(1);
    const [limit, setLimit] = useState(10);
    const [search, setSearch] = useState("");
    const [sortBy, setSortBy] = useState("created_at");
    const [sortOrder, setSortOrder] = useState("desc");

    const {
        data,
        isLoading,
        isFetching,
        isError,
        error,
    } = useQuery({
        queryKey: [
            "students",
            page,
            limit,
            search,
            sortBy,
            sortOrder,
        ],
        queryFn: () =>
            studentApis.getStudents(
                page,
                limit,
                search,
                sortBy,
                sortOrder
            ),
        placeholderData: (previousData) => previousData,
    });

    const students = data?.students || [];
    const total = data?.pagination.total || 0;
    console.log("total: ", total);
    const totalPages = Math.ceil(total / limit);

    const handleSort = (field) => {
        if (sortBy === field) {
            setSortOrder((prev) =>
                prev === "asc" ? "desc" : "asc"
            );
        } else {
            setSortBy(field);
            setSortOrder("asc");
        }

        setPage(1);
    };

    if (isLoading) {
        return <h2>Loading Students...</h2>;
    }

    if (isError) {
        return <h2>{error.message}</h2>;
    }

    return (
        <div style={{ padding: 20 }}>
            <h2>Students</h2>

            {/* Search */}
            <div
                style={{
                    display: "flex",
                    gap: 15,
                    marginBottom: 20,
                }}
            >
                <input
                    type="text"
                    placeholder="Search student..."
                    value={search}
                    onChange={(e) => {
                        setSearch(e.target.value);
                        setPage(1);
                    }}
                    style={{
                        width: 300,
                        padding: 8,
                    }}
                />

                <select
                    value={limit}
                    onChange={(e) => {
                        setLimit(Number(e.target.value));
                        setPage(1);
                    }}
                >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                </select>

                {isFetching && <span>Updating...</span>}
            </div>

            {/* Table */}
            <table
                border="1"
                cellPadding="10"
                cellSpacing="0"
                width="100%"
            >
                <thead>
                    <tr>
                        <th
                            style={{ cursor: "pointer" }}
                            onClick={() =>
                                handleSort("full_name")
                            }
                        >
                            Name{" "}
                            {sortBy === "full_name" &&
                                (sortOrder === "asc"
                                    ? "▲"
                                    : "▼")}
                        </th>

                        <th
                            style={{ cursor: "pointer" }}
                            onClick={() =>
                                handleSort(
                                    "registration_number"
                                )
                            }
                        >
                            Registration{" "}
                            {sortBy ===
                                "registration_number" &&
                                (sortOrder === "asc"
                                    ? "▲"
                                    : "▼")}
                        </th>

                        <th
                            style={{ cursor: "pointer" }}
                            onClick={() =>
                                handleSort("department")
                            }
                        >
                            Department{" "}
                            {sortBy === "department" &&
                                (sortOrder === "asc"
                                    ? "▲"
                                    : "▼")}
                        </th>

                        <th
                            style={{ cursor: "pointer" }}
                            onClick={() =>
                                handleSort("email")
                            }
                        >
                            Email{" "}
                            {sortBy === "email" &&
                                (sortOrder === "asc"
                                    ? "▲"
                                    : "▼")}
                        </th>

                        <th
                            style={{ cursor: "pointer" }}
                            onClick={() =>
                                handleSort(
                                    "semester"
                                )
                            }
                        >
                            Semester{" "}
                            {sortBy ===
                                "semester" &&
                                (sortOrder === "asc"
                                    ? "▲"
                                    : "▼")}
                        </th>

                        <th>
                            Embedding Status
                        </th>
                    </tr>
                </thead>

                <tbody>
                    {students.length === 0 ? (
                        <tr>
                            <td
                                colSpan="4"
                                align="center"
                            >
                                No Students Found
                            </td>
                        </tr>
                    ) : (
                        students.map((student) => (
                            <Link to={`/students/${student.id}`} key={student.id}>
                                <tr key={student.id}>
                                    <td><img src={student.profile_image} alt="Error" /></td>
                                    <td>{student.full_name}</td>
                                    <td>
                                        {
                                            student.registration_number
                                        }
                                    </td>
                                    <td>{student.department}</td>
                                    <td>{student.email}</td>
                                    <td>{student.semester}</td>
                                    <td>
                                        {student.face_embeddings?.some(
                                            (face) => face.embedding?.length > 0
                                        )
                                            ? "Embedded"
                                            : "Not Embedded"}
                                    </td>
                                </tr></Link>
                        ))
                    )}
                </tbody>
            </table>

            {/* Footer */}
            <div
                style={{
                    display: "flex",
                    justifyContent:
                        "space-between",
                    alignItems: "center",
                    marginTop: 20,
                }}
            >
                <span>
                    Showing{" "}
                    {students.length === 0
                        ? 0
                        : (page - 1) * limit + 1}
                    -
                    {Math.min(page * limit, total)} of{" "}
                    {total}
                </span>

                <div
                    style={{
                        display: "flex",
                        gap: 10,
                    }}
                >
                    <button
                        disabled={page === 1}
                        onClick={() =>
                            setPage((prev) => prev - 1)
                        }
                    >
                        Previous
                    </button>

                    <span>
                        Page {page} of {totalPages || 1}
                    </span>

                    <button
                        disabled={
                            page >= totalPages
                        }
                        onClick={() =>
                            setPage((prev) => prev + 1)
                        }
                    >
                        Next
                    </button>
                </div>
            </div>
        </div>
    );
}