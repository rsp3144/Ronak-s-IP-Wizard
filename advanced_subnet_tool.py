import streamlit as st
import ipaddress
import pandas as pd

st.set_page_config(page_title="Advanced Subnet Calculator", layout="centered")
st.title("📡 Advanced Subnet Calculator")

# Inputs
base_network = st.text_input("Enter base network (e.g., 101.0.0.0/8)", "101.0.0.0/8")
subnet_prefix = st.number_input("Enter new subnet prefix (CIDR)", min_value=8, max_value=30, value=19)
start_index = st.number_input("Start subnet index", min_value=1, value=1)
count = st.number_input("How many subnets to list?", min_value=1, max_value=100, value=5)

# On button click
if st.button("Generate Subnet Table"):
    try:
        base = ipaddress.ip_network(base_network)
        subnets = list(base.subnets(new_prefix=subnet_prefix))

        if start_index + count - 1 > len(subnets):
            st.error(f"Only {len(subnets)} subnets available in this block. Try a lower range.")
        else:
            data = []
            for i in range(start_index - 1, start_index - 1 + count):
                net = subnets[i]
                hosts = list(net.hosts())
                data.append({
                    "Subnet #": i + 1,
                    "Network": str(net.network_address),
                    "Usable Start": str(hosts[0]),
                    "Usable End": str(hosts[-1]),
                    "Broadcast": str(net.broadcast_address),
                    "Usable Hosts": len(hosts)
                })

            df = pd.DataFrame(data)
            st.dataframe(df)

            # Download button
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "subnets.csv", "text/csv")

            # Visual
            st.subheader("📊 Subnet Range Overview")
            st.bar_chart(df["Usable Hosts"])
    except Exception as e:
        st.error(f"Whoops! {e}")
