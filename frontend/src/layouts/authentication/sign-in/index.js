import { useState } from "react";
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import BasicLayout from "layouts/authentication/components/BasicLayout";
function Basic() {
  const [shopName, setShopName] = useState("");
  const handleSignIn = () => {
    if (shopName) {
      localStorage.setItem("shop_name", shopName);
      window.location.href = `http://localhost:8000/shops/install?shop=${shopName}`;
    }
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
            Sign in with Shopify
          </MDTypography>
        </MDBox>
        <MDBox pt={10} pb={10} px={3}>
          <MDBox component="form" role="form">
            <MDBox mb={2}>
              <MDInput
                type="text"
                label="Shop Name (e.g. my-shop.myshopify.com)"
                fullWidth
                value={shopName}
                onChange={(e) => setShopName(e.target.value)}
                sx={{
                  "& .MuiInputBase-root": {
                    height: "50px",
                    fontSize: "1.1rem",
                  },
                  "& .MuiInputLabel-root": {
                    fontSize: "1rem",
                  },
                }}
              />
            </MDBox>
            <MDBox mt={4} mb={1}>
              <MDButton variant="gradient" color="info" fullWidth onClick={handleSignIn}>
                sign in
              </MDButton>
            </MDBox>
          </MDBox>
        </MDBox>
      </Card>
    </BasicLayout>
  );
}
export default Basic;
