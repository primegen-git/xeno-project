import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import CoverLayout from "layouts/authentication/components/CoverLayout";
import axios from "axios";

function Cover() {
  const navigate = useNavigate();
  const [shop, setShop] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignUp = async () => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/auth/signup`, {
        shop,
        email,
        password,
      });

      if (response.data.success) {
        const userId = response.data.user_id;
        window.location.href = `${process.env.REACT_APP_BACKEND_URL}/shops/install?shop=${shop}&user_id=${userId}`;
      }
    } catch (error) {
      console.error("Signup failed", error);
      alert("Signup failed. Please try again.");
    }
  };

  return (
    <CoverLayout>
      <Card>
        <MDBox
          variant="gradient"
          bgColor="info"
          borderRadius="lg"
          coloredShadow="success"
          mx={2}
          mt={-3}
          p={3}
          mb={1}
          textAlign="center"
        >
          <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
            Sign Up
          </MDTypography>
        </MDBox>
        <MDBox pt={4} pb={3} px={3}>
          <MDBox component="form" role="form">
            <MDBox mb={2}>
              <MDInput
                type="text"
                label="Shop Name (e.g. my-shop.myshopify.com)"
                variant="standard"
                fullWidth
                value={shop}
                onChange={(e) => setShop(e.target.value)}
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
            <MDBox mb={2}>
              <MDInput
                type="email"
                label="Email"
                variant="standard"
                fullWidth
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
            <MDBox mb={2}>
              <MDInput
                type="password"
                label="Password"
                variant="standard"
                fullWidth
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
              <MDButton variant="gradient" color="info" fullWidth onClick={handleSignUp}>
                sign up
              </MDButton>
            </MDBox>
            <MDBox mt={2} mb={1}>
              <MDButton
                variant="outlined"
                color="info"
                fullWidth
                onClick={() => navigate("/authentication/sign-in", { state: { demo: true } })}
              >
                Click for Demo
              </MDButton>
            </MDBox>
            <MDBox mt={3} mb={1} textAlign="center">
              <MDTypography variant="button" color="text">
                Already have an account?{" "}
                <MDTypography
                  component={Link}
                  to="/authentication/sign-in"
                  variant="button"
                  color="info"
                  fontWeight="medium"
                  textGradient
                >
                  Sign In
                </MDTypography>
              </MDTypography>
            </MDBox>
          </MDBox>
        </MDBox>
      </Card>
    </CoverLayout>
  );
}
export default Cover;
