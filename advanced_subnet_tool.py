import streamlit as st
import ipaddress
import math
import pandas as pd

st.set_page_config(page_title="Subnet Calculator with Explanation", layout="centered")
st.title("📡 Subnet Calculator with Full Explanation")

# --------- INPUTS (Only 2) ---------
base_network_input = st.text_input("1️⃣ Enter base network (e.g., 101.0.0.0/8)", "101.0.0.0/8")
subnet_count = st.number_input("2️⃣ How many subnets to list?", min_value=1, max_value=2048, value=8)

# --------- CALCULATIONS ---------
if base_network_input and subnet_count:
    try:
        network = ipaddress.ip_network(base_network_input, strict=False)
        original_prefix = network.prefixlen

        # 1. Determine how many bits to borrow
        bits_borrowed = math.ceil(math.log2(subnet_count))
        new_prefix = original_prefix + bits_borrowed

        # 2. New Subnet Mask
        subnet_mask = ipaddress.IPv4Network(f"0.0.0.0/{new_prefix}").netmask.exploded

        # 3. Subnet Increment
        octets = subnet_mask.split(".")
        if new_prefix > 24:
            increment = 256 - int(octets[3])
            octet_level = "4th"
        elif new_prefix > 16:
            increment = 256 - int(octets[2])
            octet_level = "3rd"
        elif new_prefix > 8:
            increment = 256 - int(octets[1])
            octet_level = "2nd"
        else:
            increment = 256 - int(octets[0])
            octet_level = "1st"

        # 4. Hosts per Subnet
        host_bits = 32 - new_prefix
        total_hosts = 2 ** host_bits
        usable_hosts = total_hosts - 2

        # --------- SUBNETTING CALCULATIONS SECTION ---------
        st.subheader("📘 Subnetting Calculations")

        st.markdown(f"**1. Original CIDR Prefix:** /{original_prefix}  \n"
                    f"> The starting network mask provided in the input.")

        st.markdown(f"**2. New Subnet Prefix (CIDR):** /{new_prefix}  \n"
                    f"> Since we need at least {subnet_count} subnets, we find the smallest power of 2 ≥ {subnet_count}.  \n"
                    f"> 2^{bits_borrowed} = {2 ** bits_borrowed}, so we borrow {bits_borrowed} bits from the host portion.")

        st.markdown(f"**3. Bits Borrowed:** {bits_borrowed}  \n"
                    f"> These bits increase the subnet count from 1 to {2 ** bits_borrowed}.")

        st.markdown(f"**4. Subnet Mask:** {subnet_mask}  \n"
                    f"> Equivalent to /{new_prefix}, giving each subnet its boundary and size.")

        st.markdown(f"**5. Subnet Increment:** {increment} (in the {octet_level} octet)  \n"
                    f"> This tells us how far apart each subnet’s network address is from the next.")

        st.markdown(f"**6. Usable Hosts per Subnet:** {usable_hosts}  \n"
                    f"> Each subnet has 2^{host_bits} addresses. Minus network and broadcast, that’s {usable_hosts} usable hosts.")

        # --------- OPTIONAL: Show Subnet Table ---------
        st.divider()
        st.subheader("📊 Example: First N Subnets")

        subnets = list(network.subnets(new_prefix=new_prefix))
        max_available = len(subnets)

        if subnet_count > max_available:
            st.error(f"Only {max_available} subnets available from {base_network_input}. Try a smaller number.")
        else:
            rows = []
            for i in range(min(subnet_count, max_available)):
                net = subnets[i]
                hosts = list(net.hosts())
                rows.append({
                    "Subnet #": i + 1,
                    "Network": str(net.network_address),
                    "Usable Start": str(hosts[0]),
                    "Usable End": str(hosts[-1]),
                    "Broadcast": str(net.broadcast_address),
                    "Usable Hosts": len(hosts)
                })

            df = pd.DataFrame(rows)
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Subnet Table as CSV", csv, file_name="subnet_table.csv")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
