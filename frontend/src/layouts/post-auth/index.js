import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import Card from "@mui/material/Card";
import CircularProgress from "@mui/material/CircularProgress";
import BasicLayout from "layouts/authentication/components/BasicLayout";
import axios from "axios";
function PostAuth() {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState("Checking...");
  const [showOptions, setShowOptions] = useState(false);
  const [shop, setShop] = useState("");
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const isLogin = queryParams.get("is_login");
    const storedShop = localStorage.getItem("shop_name");
    setShop(storedShop);

    if (isLogin === "true") {
      // Login -> Show Options
      setShowOptions(true);
      setStatus("Welcome back! Choose an option.");
    } else if (isLogin === "false") {
      // Signup -> Auto Sync
      if (storedShop) {
        startSync(storedShop);
      } else {
        setStatus("Error: Shop name missing.");
      }
    } else {
      // Fallback or error state
      setStatus("Unknown state.");
    }
  }, [location]);
  const fetchDashboardData = async () => {
    try {
      const [
        customersRes,
        productsRes,
        ordersRes,
        topCustomersRes,
        salesByMonthRes,
        ordersByMonthRes,
      ] = await Promise.all([
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/total_customers`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/total_products`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/total_orders`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/top_customers`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/sales_by_month`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/orders_by_month`, {
          withCredentials: true,
        }),
      ]);
      return {
        stats: {
          customers: customersRes.data,
          products: productsRes.data,
          orders: ordersRes.data,
        },
        topCustomers: topCustomersRes.data.data || [],
        salesByMonth: salesByMonthRes.data,
        ordersByMonth: ordersByMonthRes.data,
      };
    } catch (error) {
      console.error("Error fetching dashboard data", error);
      return null;
    }
  };
  const startSync = async (shopName) => {
    setStatus("Syncing data...");
    setShowOptions(false);
    setLoading(true);
    try {
      await axios.get(`${process.env.REACT_APP_BACKEND_URL}/sync/customers?shop=${shopName}`, {
        withCredentials: true,
      });
      await axios.get(`${process.env.REACT_APP_BACKEND_URL}/sync/products?shop=${shopName}`, {
        withCredentials: true,
      });
      await axios.get(`${process.env.REACT_APP_BACKEND_URL}/sync/orders?shop=${shopName}`, {
        withCredentials: true,
      });
      setStatus("Sync complete! Fetching latest data...");
      const data = await fetchDashboardData();
      setStatus("Redirecting...");
      setTimeout(() => navigate("/dashboard", { state: { data } }), 500);
    } catch (error) {
      console.error("Sync failed", error);
      setStatus("Sync failed. Please try again.");
      setShowOptions(true);
      setLoading(false);
    }
  };
  const handleFetch = async () => {
    setStatus("Preparing your dashboard...");
    setShowOptions(false);
    setLoading(true);
    const data = await fetchDashboardData();
    setTimeout(() => {
      navigate("/dashboard", { state: { data } });
    }, 500);
  };
  return (
    <BasicLayout>
      <Card>
        <MDBox
          variant="gradient"
          bgColor="info"
          borderRadius="lg"
          coloredShadow="info"
          mx={2}
          mt={-3}
          p={2}
          mb={1}
          textAlign="center"
        >
          <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
            {status}
          </MDTypography>
        </MDBox>
        <MDBox pt={4} pb={3} px={3} textAlign="center">
          {loading ? (
            <CircularProgress color="info" />
          ) : (
            showOptions && (
              <MDBox display="flex" justifyContent="space-between">
                <MDButton variant="gradient" color="info" onClick={() => startSync(shop)}>
                  Sync Data
                </MDButton>
                <MDButton variant="outlined" color="info" onClick={handleFetch}>
                  Fetch Data
                </MDButton>
              </MDBox>
            )
          )}
        </MDBox>
      </Card>
    </BasicLayout>
  );
}
export default PostAuth;
