import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import SimpleLineChart from "examples/Charts/LineCharts/SimpleLineChart";
import Projects from "layouts/dashboard/components/Projects";
function Dashboard() {
  const { state } = useLocation();
  const [stats, setStats] = useState({
    customers: 0,
    products: 0,
    orders: 0,
  });
  const [topCustomers, setTopCustomers] = useState([]);
  useEffect(() => {
    if (state?.data) {
      setStats(state.data.stats);
      setTopCustomers(state.data.topCustomers);
    } else {
      const fetchData = async () => {
        try {
          const [customersRes, productsRes, ordersRes, topCustomersRes] = await Promise.all([
            axios.get("http://localhost:8000/fetch/total_customers", { withCredentials: true }),
            axios.get("http://localhost:8000/fetch/total_products", { withCredentials: true }),
            axios.get("http://localhost:8000/fetch/total_orders", { withCredentials: true }),
            axios.get("http://localhost:8000/fetch/top_customers", { withCredentials: true }),
          ]);
          setStats({
            customers: customersRes.data,
            products: productsRes.data,
            orders: ordersRes.data,
          });
          setTopCustomers(topCustomersRes.data.data || []);
        } catch (error) {
          console.error("Error fetching dashboard data", error);
        }
      };
      fetchData();
    }
  }, [state]);
  const ordersChartData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    datasets: [
      {
        label: "Orders",
        color: "info",
        data: [50, 40, 300, 220, 500, 250, 400, 230, 500, 350, 400, 600],
      },
    ],
  };
  const revenueChartData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    datasets: [
      {
        label: "Revenue",
        color: "success",
        data: [1000, 2000, 1500, 3000, 2500, 4000, 3500, 5000, 4500, 6000, 5500, 7000],
      },
    ],
  };
  return (
    <DashboardLayout>
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="people"
                title="Total Customers"
                count={stats.customers}
                percentage={{ color: "success", amount: "", label: "Updated just now" }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="inventory_2"
                title="Total Products"
                count={stats.products}
                percentage={{ color: "success", amount: "", label: "Updated just now" }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="shopping_cart"
                title="Total Orders"
                count={stats.orders}
                percentage={{ color: "success", amount: "", label: "Updated just now" }}
              />
            </MDBox>
          </Grid>
        </Grid>
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <MDBox mb={3}>
                <SimpleLineChart
                  color="info"
                  title="Orders"
                  description="Last 12 Months"
                  chart={ordersChartData}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6}>
              <MDBox mb={3}>
                <SimpleLineChart
                  color="success"
                  title="Revenue"
                  description="Last 12 Months"
                  chart={revenueChartData}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
        <MDBox>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Projects topCustomers={topCustomers} />
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}
export default Dashboard;
