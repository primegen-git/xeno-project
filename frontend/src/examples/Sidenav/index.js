import { useEffect, useState } from "react";
import { useLocation, NavLink } from "react-router-dom";
import axios from "axios";
import PropTypes from "prop-types";
import List from "@mui/material/List";
import Divider from "@mui/material/Divider";
import Link from "@mui/material/Link";
import Icon from "@mui/material/Icon";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import SidenavCollapse from "examples/Sidenav/SidenavCollapse";
import SidenavRoot from "examples/Sidenav/SidenavRoot";
import sidenavLogoLabel from "examples/Sidenav/styles/sidenav";
import {
  useMaterialUIController,
  setMiniSidenav,
  setTransparentSidenav,
  setWhiteSidenav,
} from "context";
function Sidenav({ color, brand, brandName, routes, ...rest }) {
  const [controller, dispatch] = useMaterialUIController();
  const { miniSidenav, transparentSidenav, whiteSidenav, darkMode, sidenavColor } = controller;
  const location = useLocation();
  const collapseName = location.pathname.replace("/", "");
  let textColor = "white";
  if (transparentSidenav || (whiteSidenav && !darkMode)) {
    textColor = "dark";
  } else if (whiteSidenav && darkMode) {
    textColor = "inherit";
  }
  const closeSidenav = () => setMiniSidenav(dispatch, true);
  useEffect(() => {
    function handleMiniSidenav() {
      setMiniSidenav(dispatch, window.innerWidth < 1200);
      setTransparentSidenav(dispatch, window.innerWidth < 1200 ? false : transparentSidenav);
      setWhiteSidenav(dispatch, window.innerWidth < 1200 ? false : whiteSidenav);
    }
    window.addEventListener("resize", handleMiniSidenav);
    handleMiniSidenav();
    return () => window.removeEventListener("resize", handleMiniSidenav);
  }, [dispatch, location]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [webhooks, setWebhooks] = useState({
    orders: false,
    products: false,
    customers: false,
  });

  useEffect(() => {
    const checkAuth = () => {
      const shopName = localStorage.getItem("shop_name");
      setIsLoggedIn(!!shopName);
    };

    const checkWebhooks = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/webhooks/check`, {
          withCredentials: true,
        });
        if (response.data) {
          setWebhooks({
            orders: !!response.data.orders,
            products: !!response.data.products,
            customers: !!response.data.customers,
          });
        }
      } catch (error) {
        console.error("Failed to check webhooks", error);
      }
    };

    window.addEventListener("auth-change", checkAuth);
    checkAuth();

    if (isLoggedIn) {
      checkWebhooks();
    }

    return () => window.removeEventListener("auth-change", checkAuth);
  }, [location, isLoggedIn]);

  const toggleWebhook = async (resource) => {
    const isRegistered = webhooks[resource];
    try {
      if (isRegistered) {
        // Delete
        // Resource name mapping: orders -> order, products -> product, customers -> customer
        const endpoint = resource.slice(0, -1);
        await axios.delete(`${process.env.REACT_APP_BACKEND_URL}/webhooks/${endpoint}`, {
          withCredentials: true,
        });
      } else {
        // Register
        // Resource name mapping: orders -> order, products -> product, customers -> customer
        const endpoint = resource.slice(0, -1);
        await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/webhooks/register/${endpoint}/create`,
          {
            withCredentials: true,
          }
        );
      }
      // Toggle state locally on success
      setWebhooks((prev) => ({ ...prev, [resource]: !isRegistered }));
    } catch (error) {
      console.error(`Failed to toggle webhook ${resource}`, error);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.get(`${process.env.REACT_APP_BACKEND_URL}/auth/logout`, {
        withCredentials: true,
      });
    } catch (error) {
      console.error("Logout failed", error);
    }
    localStorage.removeItem("shop_name");
    window.dispatchEvent(new Event("auth-change"));
    setIsLoggedIn(false);
    window.location.href = "/authentication/sign-in";
  };

  const renderRoutes = routes.map(({ type, name, icon, title, noCollapse, key, href, route }) => {
    if (isLoggedIn && (key === "sign-in" || key === "sign-up")) {
      return null;
    }

    let returnValue;

    if (type === "collapse") {
      returnValue = href ? (
        <Link
          href={href}
          key={key}
          target="_blank"
          rel="noreferrer"
          sx={{ textDecoration: "none" }}
        >
          <SidenavCollapse
            name={name}
            icon={icon}
            active={key === collapseName}
            noCollapse={noCollapse}
          />
        </Link>
      ) : (
        <NavLink key={key} to={route}>
          <SidenavCollapse name={name} icon={icon} active={key === collapseName} />
        </NavLink>
      );
    } else if (type === "title") {
      returnValue = (
        <MDTypography
          key={key}
          color={textColor}
          display="block"
          variant="caption"
          fontWeight="bold"
          textTransform="uppercase"
          pl={3}
          mt={2}
          mb={1}
          ml={1}
        >
          {title}
        </MDTypography>
      );
    } else if (type === "divider") {
      returnValue = (
        <Divider
          key={key}
          light={
            (!darkMode && !whiteSidenav && !transparentSidenav) ||
            (darkMode && !transparentSidenav && whiteSidenav)
          }
        />
      );
    }

    return returnValue;
  });

  return (
    <SidenavRoot
      {...rest}
      variant="permanent"
      ownerState={{ transparentSidenav, whiteSidenav, miniSidenav, darkMode }}
    >
      <MDBox pt={3} pb={1} px={4}>
        <MDBox
          width={!brandName && "100%"}
          sx={(theme) => ({
            ...sidenavLogoLabel(theme, { miniSidenav }),
            ml: 0, // Override default margin
            textAlign: "center",
          })}
        >
          <MDTypography component="h3" variant="h6" fontWeight="medium" color={textColor}>
            {brandName}
          </MDTypography>
        </MDBox>
      </MDBox>
      <Divider
        light={
          (!darkMode && !whiteSidenav && !transparentSidenav) ||
          (darkMode && !transparentSidenav && whiteSidenav)
        }
      />
      <List>{renderRoutes}</List>
      {isLoggedIn && (
        <MDBox p={2} mt="auto" display="flex" flexDirection="column">
          <MDButton
            variant="gradient"
            color={webhooks.orders ? "error" : "info"}
            fullWidth
            onClick={() => toggleWebhook("orders")}
            sx={{ mb: 1, fontSize: "0.75rem" }}
          >
            {webhooks.orders ? "Remove Orders Webhook" : "Add Orders Webhook"}
          </MDButton>
          <MDButton
            variant="gradient"
            color={webhooks.products ? "error" : "info"}
            fullWidth
            onClick={() => toggleWebhook("products")}
            sx={{ mb: 1, fontSize: "0.75rem" }}
          >
            {webhooks.products ? "Remove Products Webhook" : "Add Products Webhook"}
          </MDButton>
          <MDButton
            variant="gradient"
            color={webhooks.customers ? "error" : "info"}
            fullWidth
            onClick={() => toggleWebhook("customers")}
            sx={{ mb: 2, fontSize: "0.75rem" }}
          >
            {webhooks.customers ? "Remove Customers Webhook" : "Add Customers Webhook"}
          </MDButton>
          <MDButton variant="gradient" color="error" fullWidth onClick={handleLogout}>
            Logout
          </MDButton>
        </MDBox>
      )}
    </SidenavRoot>
  );
}
Sidenav.defaultProps = {
  color: "info",
  brand: "",
};
Sidenav.propTypes = {
  color: PropTypes.oneOf(["primary", "secondary", "info", "success", "warning", "error", "dark"]),
  brand: PropTypes.string,
  brandName: PropTypes.string.isRequired,
  routes: PropTypes.arrayOf(PropTypes.object).isRequired,
};
export default Sidenav;
