import { useState } from "react";
import PropTypes from "prop-types";

// @mui material components
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 React examples
import DataTable from "examples/Tables/DataTable";

// Data

function Projects({ topCustomers }) {
  const columns = [
    { Header: "Customer", accessor: "customer", width: "45%", align: "left" },
    { Header: "Email", accessor: "email", align: "left" },
    { Header: "Total Spent", accessor: "total_spent", align: "center" },
    { Header: "Total Quantity", accessor: "total_quantity", align: "center" },
  ];

  const rows = (topCustomers || []).map((customer) => ({
    customer: (
      <MDBox display="flex" alignItems="center" lineHeight={1}>
        <MDTypography variant="button" fontWeight="medium" ml={1} lineHeight={1}>
          {customer.first_name} {customer.last_name}
        </MDTypography>
      </MDBox>
    ),
    email: (
      <MDTypography variant="caption" color="text" fontWeight="medium">
        {customer.email}
      </MDTypography>
    ),
    total_spent: (
      <MDTypography variant="caption" color="text" fontWeight="medium">
        {customer.total_price}
      </MDTypography>
    ),
    total_quantity: (
      <MDTypography variant="caption" color="text" fontWeight="medium">
        {customer.total_quantity}
      </MDTypography>
    ),
  }));

  return (
    <Card>
      <MDBox display="flex" justifyContent="space-between" alignItems="center" p={3}>
        <MDBox>
          <MDTypography variant="h4" gutterBottom>
            Top Customers
          </MDTypography>
        </MDBox>
      </MDBox>
      <MDBox>
        <DataTable
          table={{ columns, rows }}
          showTotalEntries={false}
          isSorted={false}
          noEndBorder
          entriesPerPage={false}
        />
      </MDBox>
    </Card>
  );
}

Projects.propTypes = {
  topCustomers: PropTypes.arrayOf(PropTypes.object),
};

export default Projects;
