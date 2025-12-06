import { useState } from "react";
import axios from "axios";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import TextField from "@mui/material/TextField";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DataTable from "examples/Tables/DataTable";
function FilterByDate() {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [rows, setRows] = useState([]);
  const columns = [
    { Header: "Order ID", accessor: "id", align: "left" },
    { Header: "Customer ID", accessor: "customer_id", align: "left" },
    { Header: "Variant ID", accessor: "variant_id", align: "left" },
    { Header: "Quantity", accessor: "quantity", align: "center" },
    { Header: "Created At", accessor: "created_at", align: "center" },
  ];
  const handleFilter = async () => {
    try {
      let query = "";
      if (startDate) query += `?start_date=${startDate}`;
      if (endDate) query += `${query ? "&" : "?"}end_date=${endDate}`;
      const response = await axios.get(`http://localhost:8000/fetch/orders${query}`, {
        withCredentials: true,
      });
      const formattedRows = response.data.map((order) => ({
        id: order.id,
        customer_id: order.customer_id,
        variant_id: order.variant_id,
        quantity: order.quantity,
        created_at: new Date(order.created_at).toLocaleString(),
      }));
      setRows(formattedRows);
    } catch (error) {
      console.error("Error fetching orders", error);
    }
  };
  return (
    <DashboardLayout>
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDTypography variant="h6" color="white">
                  Filter Orders by Date
                </MDTypography>
              </MDBox>
              <MDBox p={3}>
                <MDBox display="flex" alignItems="center" mb={3} gap={2}>
                  <TextField
                    label="Start Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                  <TextField
                    label="End Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                  <MDButton variant="gradient" color="info" onClick={handleFilter}>
                    Filter
                  </MDButton>
                </MDBox>
                {rows.length > 0 ? (
                  <DataTable
                    table={{ columns, rows }}
                    isSorted={false}
                    entriesPerPage={false}
                    showTotalEntries={false}
                    noEndBorder
                  />
                ) : (
                  <MDTypography variant="button" color="text" fontWeight="regular">
                    No orders found. Select a date range and click Filter.
                  </MDTypography>
                )}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
    </DashboardLayout>
  );
}
export default FilterByDate;
