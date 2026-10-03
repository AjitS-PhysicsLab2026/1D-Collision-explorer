import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 👤 ADD YOUR NAME HERE
# ==========================================
DEVELOPER_NAME = "Ajit Salunkhe"  # Replace with your real name

# --- Page Configuration ---
st.set_page_config(
    page_title="Ajit's Collision Simulation Lab",
    page_icon="⚽",
    layout="wide"
)

# --- Header with Your Name ---
st.title("⚽ Ajit's Collision Simulation Lab")
st.caption(f"🎓 **Developed by:** {DEVELOPER_NAME}")
st.markdown("Select a simulation mode in the sidebar to dynamically study kinematic behaviors with real-time analytics.")

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Simulation Controls")
sim_mode = st.sidebar.radio(
    "Select Simulation Mode:",
    ["1D Horizontal Collision", "Vertical Free Fall & Bounce"]
)

st.sidebar.markdown("---")

if sim_mode == "1D Horizontal Collision":
    # --- Horizontal Mode Inputs ---
    col_sb1, col_sb2 = st.sidebar.columns(2)
    with col_sb1:
        st.subheader("Body 1 (Blue)")
        m1 = st.number_input("Mass m1 (kg)", min_value=0.5, max_value=50.0, value=5.0, step=0.5)
        u1 = st.number_input("Vel u1 (px/s)", min_value=-400.0, max_value=400.0, value=180.0, step=10.0)

    with col_sb2:
        st.subheader("Body 2 (Orange)")
        m2 = st.number_input("Mass m2 (kg)", min_value=0.5, max_value=50.0, value=3.0, step=0.5)
        u2 = st.number_input("Vel u2 (px/s)", min_value=-400.0, max_value=400.0, value=60.0, step=10.0)

    st.sidebar.markdown("---")
    e = st.sidebar.slider("Coefficient of Restitution (e)", min_value=0.0, max_value=1.0, value=0.75, step=0.05)

    # --- Physics Calculations (Horizontal) ---
    def calculate_final_velocities(m1, m2, u1, u2, e):
        total_mass = m1 + m2
        if total_mass == 0: return 0.0, 0.0
        v1 = ((m1 - e * m2) * u1 + m2 * u2 * (1 + e)) / total_mass
        # FIX: Changed the accidental 'v2' to 'u2' on the right side of the expression below
        v2 = (m1 * u1 * (1 + e) + (m2 - e * m1) * u2) / total_mass
        return v1, v2

    v1, v2 = calculate_final_velocities(m1, m2, u1, u2, e)
    p_init, ke_init = m1*u1 + m2*u2, 0.5*m1*(u1**2) + 0.5*m2*(u2**2)
    p_final, ke_final = m1*v1 + m2*v2, 0.5*m1*(v1**2) + 0.5*m2*(v2**2)
    ke_lost = max(0.0, ke_init - ke_final)
    ke_lost_pct = (ke_lost / ke_init) * 100.0 if ke_init > 0 else 0.0

    # --- Dashboard (Horizontal) ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final Velocity v1", f"{v1:.1f} px/s", delta=f"{v1 - u1:.1f}")
    c2.metric("Final Velocity v2", f"{v2:.1f} px/s", delta=f"{v2 - u2:.1f}")
    c3.metric("Total Momentum (P)", f"{p_final:.1f}", delta="Conserved")
    c4.metric("KE Lost", f"{ke_lost:.1f} J", delta=f"-{ke_lost_pct:.1f}%", delta_color="inverse")

    # --- HTML Injection (Horizontal Canvas) ---
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #f5f7fa; font-family: Arial, sans-serif; text-align: center; }}
            canvas {{ background: #ffffff; border: 2px solid #34495e; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            button {{ margin-top: 10px; padding: 8px 18px; font-size: 14px; font-weight: bold; color: white; background-color: #2980b9; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background-color: #1f618d; }}
        </style>
    </head>
    <body>
        <canvas id="simCanvas" width="800" height="250"></canvas><br>
        <button onclick="resetSimulation()">🔁 Restart Animation</button>
        <script>
            const canvas = document.getElementById("simCanvas");
            const ctx = canvas.getContext("2d");
            const devName = "{DEVELOPER_NAME}";
            const m1 = {m1}, m2 = {m2}, u1 = {u1}, u2 = {u2}, e = {e};
            const radius1 = Math.max(16, Math.min(35, 16 + m1 * 1.5));
            const radius2 = Math.max(16, Math.min(35, 16 + m2 * 1.5));
            const trackLeft = 30; const trackRight = 770;
            let x1, x2, v1, v2;
            let lastTime = performance.now();

            function resetSimulation() {{
                x1 = 150; x2 = 450; v1 = u1; v2 = u2;
                lastTime = performance.now();
            }}
            function animate(now) {{
                let dt = (now - lastTime) / 1000.0; lastTime = now;
                if (dt > 0.1) dt = 0.016;
                x1 += v1 * dt; x2 += v2 * dt;

                if ((x2 - x1) <= (radius1 + radius2)) {{
                    let overlap = (radius1 + radius2) - (x2 - x1);
                    x1 -= overlap / 2; x2 += overlap / 2;
                    if (v1 > v2) {{
                        let totalM = m1 + m2;
                        let nv1 = ((m1 - e * m2) * v1 + m2 * v2 * (1 + e)) / totalM;
                        let nv2 = ((m1 * v1 * (1 + e)) + (m2 - e * m1) * v2) / totalM;
                        v1 = nv1; v2 = nv2;
                    }}
                }}
                if (x1 - radius1 <= trackLeft) {{ x1 = trackLeft + radius1; if (v1 < 0) v1 = -v1 * e; }}
                if (x2 + radius2 >= trackRight) {{ x2 = trackRight - radius2; if (v2 > 0) v2 = -v2 * e; }}

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.font = "bold 13px Arial"; ctx.fillStyle = "#7f8c8d";
                ctx.fillText("SIMULATOR BY: " + devName.toUpperCase(), 590, 25);
                ctx.beginPath(); ctx.moveTo(trackLeft, 180); ctx.lineTo(trackRight, 180);
                ctx.strokeStyle = "#46505e"; ctx.lineWidth = 3; ctx.stroke();
                
                ctx.beginPath(); ctx.arc(x1, 180 - radius1, radius1, 0, Math.PI * 2); ctx.fillStyle = "#2980b9"; ctx.fill();
                ctx.beginPath(); ctx.arc(x2, 180 - radius2, radius2, 0, Math.PI * 2); ctx.fillStyle = "#e67e22"; ctx.fill();
                
                ctx.font = "14px Arial"; ctx.fillStyle = "#333333";
                ctx.fillText("Body 1 Speed: " + v1.toFixed(1) + " px/s", 30, 45);
                ctx.fillText("Body 2 Speed: " + v2.toFixed(1) + " px/s", 30, 70);
                requestAnimationFrame(animate);
            }}
            resetSimulation(); requestAnimationFrame(animate);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=320)
else:
    # --- Vertical Mode Inputs ---
    h_init = st.sidebar.number_input("Initial Height h0 (meters)", min_value=1.0, max_value=10.0, value=8.0, step=0.5)
    e_vert = st.sidebar.slider("Coefficient of Restitution (e)", min_value=0.0, max_value=1.0, value=0.8, step=0.05)
    max_bounces = st.sidebar.selectbox("Allowed Number of Bounces:", [1, 2, 3, 4, 5], index=2)
    
    # --- Physics Calculations (Vertical Analytics) ---
    g_phys = 9.81
    v_impact = (2 * g_phys * h_init) ** 0.5
    
    # Calculate the exact apex height of the final allowed bounce
    # Each bounce reduces the height by a factor of e^2
    h_bounce = h_init * (e_vert ** (2 * max_bounces))
    v_bounce = (2 * g_phys * h_bounce) ** 0.5 if max_bounces > 0 else 0.0
    
    # --- Dashboard (Vertical) ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Initial Drop Height", f"{h_init:.2f} m")
    c2.metric("Impact Speed (Pre-Bounce)", f"{v_impact:.2f} m/s")
    c3.metric(f"Upward Speed (Bounce {max_bounces})", f"{v_bounce:.2f} m/s")
    c4.metric(f"Final Rebound Height", f"{h_bounce:.2f} m", delta=f"-{(1-(h_bounce/h_init))*100:.1f}% Total Loss")

    # --- HTML Injection (Vertical Canvas with Dynamic Elastic Drop) ---
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #f5f7fa; font-family: Arial, sans-serif; text-align: center; }}
            canvas {{ background: #ffffff; border: 2px solid #2c3e50; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            button {{ margin-top: 10px; padding: 8px 18px; font-size: 14px; font-weight: bold; color: white; background-color: #27ae60; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background-color: #219653; }}
        </style>
    </head>
    <body>
        <canvas id="dropCanvas" width="800" height="400"></canvas><br>
        <button onclick="resetDrop()">🔁 Drop Sphere Again</button>
        <script>
            const canvas = document.getElementById("dropCanvas");
            const ctx = canvas.getContext("2d");
            const devName = "{DEVELOPER_NAME}";
            
            // Physics Scaling Properties
            const groundY = 350;
            const skyY = 50;
            const availableHeightPx = groundY - skyY; // 300px max mapping scale
            
            const h0_m = {h_init};
            const hFinal_m = {h_bounce};
            const e = {e_vert};
            const maxAllowedBounces = {max_bounces};
            const g = 400; // Visual gravitational scaling factor (px/s^2)
            
            const radius = 20;
            let y, vy;
            let trail = [];
            let lastTime = performance.now();
            let compressionTimer = 0;
            let bounceCount = 0;
            let simulationComplete = false;

            // Mapping heights to pixel coordinates
            const yStartPx = groundY - ((h0_m / 10.0) * availableHeightPx) - radius;
            const yFinalPx = groundY - ((hFinal_m / 10.0) * availableHeightPx) - radius;

            function resetDrop() {{
                y = yStartPx;
                vy = 0;
                trail = [];
                compressionTimer = 0;
                bounceCount = 0;
                simulationComplete = false;
                lastTime = performance.now();
            }}

            function animateDrop(now) {{
                let dt = (now - lastTime) / 1000.0;
                lastTime = now;
                if (dt > 0.1) dt = 0.016;

                if (!simulationComplete) {{
                    if (compressionTimer > 0) {{
                        compressionTimer -= dt;
                    }} else {{
                        vy += g * dt;
                        y += vy * dt;
                        
                        trail.push({{x: 400, y: y}});
                        if (trail.length > 25) trail.shift();

                        // Check collision against ground plane
                        if (y + radius >= groundY) {{
                            y = groundY - radius;
                            bounceCount++;
                            
                            if (bounceCount > maxAllowedBounces) {{
                                // Turn off simulation cleanly when bounce limit is exceeded
                                vy = 0;
                                y = groundY - radius;
                                simulationComplete = true;
                            }} else if (Math.abs(vy) > 5) {{
                                vy = -vy * e;
                                compressionTimer = 0.06; // Triggers deformation frame
                            }} else {{
                                vy = 0;
                                simulationComplete = true;
                            }}
                        }}

                        // Check if ball reached final apex on its last upward run
                        if (bounceCount === maxAllowedBounces && vy >= 0) {{
                            y = yFinalPx;
                            vy = 0;
                            simulationComplete = true;
                        }}
                    }}
                }}

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Author Watermark Stamp
                ctx.font = "bold 13px Arial"; ctx.fillStyle = "#7f8c8d";
                ctx.fillText("SIMULATOR BY: " + devName.toUpperCase(), 590, 25);
                
                // Draw background metric grids
                ctx.strokeStyle = "#f1f5f9"; ctx.lineWidth = 1;
                ctx.fillStyle = "#94a3b8"; ctx.font = "11px Arial";
                for(let i=0; i<=10; i+=2) {{
                    let markY = groundY - ((i / 10.0) * availableHeightPx);
                    ctx.beginPath(); ctx.moveTo(250, markY); ctx.lineTo(550, markY); ctx.stroke();
                    ctx.fillText(i + "m", 220, markY + 4);
                }}

                // --- PROPER DARK STATIC LINES SHOWING HEIGHT ---
                // 1. Initial Drop Height Line
                let initialLineY = groundY - ((h0_m / 10.0) * availableHeightPx);
                ctx.strokeStyle = "#1e3a8a"; ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
                ctx.beginPath(); ctx.moveTo(250, initialLineY); ctx.lineTo(550, initialLineY); ctx.stroke();
                ctx.setLineDash([]); // Reset line dash
                ctx.fillStyle = "#1e3a8a"; ctx.font = "bold 12px Arial";
                ctx.fillText("Initial Height (h0): " + h0_m.toFixed(2) + " m", 560, initialLineY + 4);

                // 2. Final Rebound Peak Height Line
                let finalLineY = groundY - ((hFinal_m / 10.0) * availableHeightPx);
                ctx.strokeStyle = "#b91c1c"; ctx.lineWidth = 2; ctx.setLineDash([4, 4]);
                ctx.beginPath(); ctx.moveTo(250, finalLineY); ctx.lineTo(550, finalLineY); ctx.stroke();
                ctx.setLineDash([]); // Reset line dash
                ctx.fillStyle = "#b91c1c"; ctx.font = "bold 12px Arial";
                ctx.fillText("Bounce " + maxAllowedBounces + " Apex (h1): " + hFinal_m.toFixed(2) + " m", 560, finalLineY + 4);

                // Draw Ground Platform Boundary
                ctx.beginPath(); ctx.moveTo(100, groundY); ctx.lineTo(700, groundY);
                ctx.strokeStyle = "#2c3e50"; ctx.lineWidth = 4; ctx.stroke();

                // Draw elegant fading motion path trail
                for(let i=0; i<trail.length; i++) {{
                    ctx.beginPath();
                    ctx.arc(trail[i].x, trail[i].y, radius * (i / trail.length), 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(39, 174, 96, ${{0.08 * (i / trail.length)}})`;
                    ctx.fill();
                }}

                // Dynamic Elastic Ball Render (Squish when impacting ground)
                ctx.beginPath();
                if (compressionTimer > 0 && !simulationComplete) {{
                    ctx.ellipse(400, groundY - (radius * 0.7), radius * 1.3, radius * 0.7, 0, 0, Math.PI * 2);
                }} else {{
                    ctx.arc(400, y, radius, 0, Math.PI * 2);
                }}
                ctx.fillStyle = "#27ae60"; ctx.fill(); ctx.strokeStyle = "#1e7e34"; ctx.lineWidth = 2; ctx.stroke();

                // Onscreen Metrics HUD Overlay
                let currentHeightM = ((groundY - radius - y) / availableHeightPx) * 10.0;
                if(currentHeightM < 0.02 || simulationComplete && y === (groundY - radius)) currentHeightM = 0.0;
                if(simulationComplete && y === yFinalPx) currentHeightM = hFinal_m;

                let currentSpeedMS = Math.abs(vy / 70.0);
                if(simulationComplete) currentSpeedMS = 0.0;

                ctx.font = "14px Arial"; ctx.fillStyle = "#2c3e50";
                ctx.fillText("Current Height: " + currentHeightM.toFixed(2) + " m", 100, 80);
                ctx.fillText("Current Velocity: " + (simulationComplete ? "STOPPED" : (vy <= 0 ? "↑ " : "↓ ") + currentSpeedMS.toFixed(2) + " m/s"), 100, 105);
                ctx.fillText("Bounces: " + bounceCount + " / " + maxAllowedBounces, 100, 130);

                requestAnimationFrame(animateDrop);
            }}
            resetDrop(); requestAnimationFrame(animateDrop);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=470)
