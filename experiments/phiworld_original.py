# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Button, Slider
from scipy.signal import convolve2d
import threading
import time
import tkinter as tk # Using Tkinter for the GUI structure
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class EmergentParticleSimulator:
    """
    Simulates a 2D Clockfield (Psi_0) with TADS-like dynamics and
    implicit WoW/Substrate influence via a biharmonic term,
    aiming to show emergent pseudo-particles.
    """
    def __init__(self, grid_size=128):
        self.grid_size = grid_size

        # --- Parameters (Tunable via GUI) ---
        self.params = {
            'dt': tk.DoubleVar(value=0.08),         # Time step
            'damping': tk.DoubleVar(value=0.001),   # Damping factor
            'base_c_sq': tk.DoubleVar(value=1.0),    # Base wave speed squared
            'tension_factor': tk.DoubleVar(value=5.0), # How much field affects speed (beta in TADS code)
            'potential_lin': tk.DoubleVar(value=1.0),  # Linear part of V' (-phi)
            'potential_cub': tk.DoubleVar(value=0.2),  # Cubic part of V' (+0.2*phi^3)
            'biharmonic_gamma': tk.DoubleVar(value=0.02),# Coefficient for laplacian(laplacian(phi)) term
            'particle_threshold': tk.DoubleVar(value=0.5), # Amplitude threshold for detecting particles
        }
        # --- Internal State ---
        self.phi = np.zeros((grid_size, grid_size), dtype=np.float64)
        self.phi_old = np.zeros_like(self.phi)
        self.t = 0.0
        self.step_count = 0
        self.particle_centers = []

        # Optimized Laplacian Kernel
        self.laplacian_kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float64)

        # --- Simulation Control ---
        self.running = False
        self.update_interval_ms = 30 # Approx 33 FPS target

        # --- Initialize ---
        self.initialize_field('gaussian_pulse') # Start with a pulse

    def initialize_field(self, mode='gaussian_pulse'):
        """Initialize the field configuration."""
        print("Initializing field...")
        if mode == 'random':
            np.random.seed(int(time.time())) # Seed with time for different random starts
            self.phi = (np.random.rand(self.grid_size, self.grid_size) - 0.5) * 0.1
        elif mode == 'gaussian_pulse':
            x = np.arange(self.grid_size)
            y = np.arange(self.grid_size)
            X, Y = np.meshgrid(x, y, indexing='ij')
            cx = cy = self.grid_size // 2
            radius = self.grid_size / 15.0
            self.phi[:] = 2.0 * np.exp(-((X - cx)**2 + (Y - cy)**2) / (2 * radius**2))
        # Add more initialization options if needed (e.g., sine waves)
        else: # Default to zeros
             self.phi = np.zeros((self.grid_size, self.grid_size), dtype=np.float64)

        self.phi_old = np.copy(self.phi)
        self.t = 0.0
        self.step_count = 0
        self.particle_centers = []
        print("Field Initialized.")


    def _laplacian(self, f):
        """Computes the discrete Laplacian using convolution with periodic boundaries."""
        return convolve2d(f, self.laplacian_kernel, mode='same', boundary='wrap')

    def _biharmonic(self, f):
        """Computes the discrete biharmonic operator (Laplacian of Laplacian)."""
        lap_f = self._laplacian(f)
        return self._laplacian(lap_f)

    def _potential_deriv(self, phi):
        """Calculates the derivative of the potential V(phi)."""
        # V'(phi) = -potential_lin * phi + potential_cub * phi^3
        return (-self.params['potential_lin'].get() * phi
                + self.params['potential_cub'].get() * (phi**3))

    def _local_speed_sq(self, phi):
        """Calculates the local wave speed squared, dependent on field intensity."""
        # c^2(phi) = base_c_sq / (1 + tension_factor * phi^2)
        intensity = phi**2
        return self.params['base_c_sq'].get() / (1.0 + self.params['tension_factor'].get() * intensity + 1e-9) # Add epsilon


    def step(self):
        """Perform one timestep of the simulation."""
        dt = self.params['dt'].get()
        damping = self.params['damping'].get()
        gamma = self.params['biharmonic_gamma'].get()

        # Calculate terms
        lap_phi = self._laplacian(self.phi)
        biharm_phi = self._biharmonic(self.phi)
        c2 = self._local_speed_sq(self.phi)
        V_prime = self._potential_deriv(self.phi)

        # Calculate acceleration (RHS of wave equation)
        # accel = c^2 * lap(phi) - V'(phi) - gamma * lap(lap(phi))
        acceleration = (c2 * lap_phi) - V_prime - (gamma * biharm_phi)

        # Update using Verlet integration (or similar finite difference)
        # phi_new = 2*phi - phi_old + dt^2 * acceleration (basic Verlet)
        # Add damping: Treat velocity implicitly: velocity = phi - phi_old
        # phi_new = phi + (1 - damping*dt)*(phi - phi_old) + dt^2 * acceleration
        velocity = self.phi - self.phi_old
        phi_new = self.phi + (1.0 - damping*dt)*velocity + (dt**2)*acceleration

        # Update fields for next step
        self.phi_old = self.phi
        self.phi = phi_new

        # Track particles (find local maxima)
        self._track_particles()

        self.t += dt
        self.step_count += 1

    def _track_particles(self):
        """Identify pseudo-particles as local maxima above a threshold."""
        threshold = self.params['particle_threshold'].get()
        maxima = []
        phi_abs = np.abs(self.phi)

        # Simple comparison with neighbors (could be optimized)
        # Padding helps handle boundaries easily
        padded_phi_abs = np.pad(phi_abs, 1, mode='wrap')

        for i in range(1, self.grid_size + 1):
            for j in range(1, self.grid_size + 1):
                val = padded_phi_abs[i, j]
                if val > threshold:
                    # Check 8 neighbors in padded array
                    is_max = (
                        val > padded_phi_abs[i-1, j-1] and val > padded_phi_abs[i-1, j] and val > padded_phi_abs[i-1, j+1] and
                        val > padded_phi_abs[i,   j-1]                                   and val > padded_phi_abs[i,   j+1] and
                        val > padded_phi_abs[i+1, j-1] and val > padded_phi_abs[i+1, j] and val > padded_phi_abs[i+1, j+1]
                    )
                    if is_max:
                        # Store original coordinates (i-1, j-1) and original field value
                        maxima.append(((j - 1), (i - 1), self.phi[i - 1, j - 1]))

        self.particle_centers = maxima


    def get_field_state(self):
        """Return current field state for plotting."""
        return self.phi

    def get_particle_locations(self):
        """Return locations and signs of detected particles."""
        return self.particle_centers

    def get_time(self):
        """Return current simulation time."""
        return self.t

    def get_step_count(self):
        """Return current step count."""
        return self.step_count

    def reset_simulation(self):
        """Reset simulation to initial state."""
        self.initialize_field('gaussian_pulse') # Or 'random'

    def update_parameter(self, param_name, value):
         """Update a simulation parameter."""
         if param_name in self.params:
             self.params[param_name].set(float(value))
             print(f"Set {param_name} to {self.params[param_name].get():.4f}")
         else:
             print(f"Warning: Unknown parameter {param_name}")


class SimulationGUI:
    """Tkinter GUI for the Emergent Particle Simulator."""
    def __init__(self, root, simulator):
        self.root = root
        self.simulator = simulator
        self.root.title("Emergent Particle Simulation (TADS+WoW Implicit)")

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # --- Plotting Setup ---
        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.im = self.ax.imshow(self.simulator.get_field_state(), cmap='viridis',
                                 vmin=-2.0, vmax=2.0, interpolation='bilinear', animated=True)
        self.particle_markers, = self.ax.plot([], [], 'o', color='red', markersize=6, alpha=0.7) # Placeholder for particles
        self.ax.set_title("Ψ₀ Field (Clockfield/Layer 0)")
        self.fig.colorbar(self.im, ax=self.ax, fraction=0.046, pad=0.04)

        # --- Tkinter Layout ---
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas Frame
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Control Frame
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(control_frame, text="Controls", font=("Arial", 14, "bold")).pack(pady=5)

        # Start/Stop Button
        self.start_stop_button = ttk.Button(control_frame, text="Start", command=self._toggle_simulation)
        self.start_stop_button.pack(fill=tk.X, pady=5)

        # Reset Button
        reset_button = ttk.Button(control_frame, text="Reset Field", command=self._reset_sim)
        reset_button.pack(fill=tk.X, pady=5)

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(control_frame, text="Parameters", font=("Arial", 12, "bold")).pack(pady=5)

        # Parameter Sliders
        self.sliders = {}
        for name, tk_var in self.simulator.params.items():
            frame = ttk.Frame(control_frame)
            frame.pack(fill=tk.X, pady=2)
            label_text = name.replace('_', ' ').title()
            # *** CORRECTION HERE: Removed width=15 from pack() ***
            ttk.Label(frame, text=f"{label_text}:").pack(side=tk.LEFT, anchor='w')
            val_label = ttk.Label(frame, text=f"{tk_var.get():.3f}", width=6)
            val_label.pack(side=tk.RIGHT, padx=5)

            # Define slider range based on parameter name (customize these)
            min_val, max_val, precision = 0.0, 1.0, 3
            if name == 'dt': min_val, max_val, precision = 0.01, 0.2, 3
            elif name == 'damping': min_val, max_val, precision = 0.0, 0.01, 4
            elif name == 'base_c_sq': min_val, max_val, precision = 0.1, 5.0, 2
            elif name == 'tension_factor': min_val, max_val, precision = 0.0, 20.0, 2
            elif name == 'potential_lin': min_val, max_val, precision = 0.1, 2.0, 2
            elif name == 'potential_cub': min_val, max_val, precision = 0.0, 1.0, 2
            elif name == 'biharmonic_gamma': min_val, max_val, precision = 0.0, 0.1, 4
            elif name == 'particle_threshold': min_val, max_val, precision = 0.1, 2.0, 2

            slider = ttk.Scale(frame, variable=tk_var, from_=min_val, to=max_val, orient='horizontal',
                               command=lambda v, n=name: self._update_param_from_gui(n, v))
            slider.pack(fill=tk.X, expand=True, side=tk.RIGHT)
            self.sliders[name] = {'var': tk_var, 'label': val_label, 'precision': precision}
            # Trigger label update when variable changes
            tk_var.trace_add("write", lambda *args, n=name: self._update_slider_display(n))

        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)

        # Status Label
        self.status_var = tk.StringVar(value="Status: Idle | Steps: 0 | Particles: 0")
        ttk.Label(control_frame, textvariable=self.status_var, wraplength=180).pack(fill=tk.X, pady=5)

        # --- Animation Control ---
        self._animation_job = None

    def _update_param_from_gui(self, name, value):
        """Callback when slider is moved."""
        # This updates the simulator's variable directly via tk_var
        # We might need to update the display label manually if trace doesn't fire instantly
        self._update_slider_display(name)
        # Optionally print or log change
        # print(f"GUI set {name} to {self.simulator.params[name].get():.4f}")


    def _update_slider_display(self, name):
         """Update the text label next to a slider."""
         if name in self.sliders:
             slider_info = self.sliders[name]
             try:
                 val = slider_info['var'].get()
                 slider_info['label'].config(text=f"{val:.{slider_info['precision']}f}")
             except tk.TclError:
                 pass # Ignore errors during shutdown

    def _update_gui(self):
        """Update the plot and status in the GUI thread."""
        if not self.simulator: return # Check if simulator exists

        # Update plot data
        field_data = self.simulator.get_field_state()
        self.im.set_data(field_data)
        # Adjust color limits dynamically or keep fixed? Fixed for stability.
        max_abs = np.max(np.abs(field_data)) if np.any(field_data) else 1.0 # Avoid error on empty/zero field
        v_limit = max(1.0, max_abs*1.1) # Ensure limit is at least 1.0
        self.im.set_clim(vmin=-v_limit, vmax=v_limit) # Dynamic limits centered at 0

        # Update particle markers
        particles = self.simulator.get_particle_locations()
        if particles:
            x_coords = [p[0] for p in particles]
            y_coords = [p[1] for p in particles]
            self.particle_markers.set_data(x_coords, y_coords)
        else:
            self.particle_markers.set_data([], [])

        # Update title and status
        self.ax.set_title(f"Ψ₀ Field @ t={self.simulator.get_time():.2f}")
        self.status_var.set(f"Status: {'Running' if self.simulator.running else 'Paused'} | "
                            f"Steps: {self.simulator.get_step_count()} | "
                            f"Particles: {len(particles)}")

        # Redraw canvas
        try:
            self.canvas.draw_idle()
        except tk.TclError:
            pass # Ignore errors if window is closing

        # Schedule next update
        if self.simulator.running:
            self._animation_job = self.root.after(self.simulator.update_interval_ms, self._update_gui)

    def _simulation_thread_func(self):
        """Target function for the simulation thread."""
        while self.simulator.running:
            t_start = time.perf_counter()
            self.simulator.step()
            t_end = time.perf_counter()

            # Simple frame rate control
            elapsed_ms = (t_end - t_start) * 1000
            sleep_ms = max(0, self.simulator.update_interval_ms - elapsed_ms)
            time.sleep(sleep_ms / 1000.0)
            # More sophisticated control might be needed if step() varies wildly

    def _toggle_simulation(self):
        """Start or stop the simulation thread."""
        if not self.simulator.running:
            self.simulator.running = True
            self.start_stop_button.config(text="Stop")
            # Start thread
            self.sim_thread = threading.Thread(target=self._simulation_thread_func, daemon=True)
            self.sim_thread.start()
            # Start GUI updates
            self._animation_job = self.root.after(self.simulator.update_interval_ms, self._update_gui)
            self.status_var.set("Status: Running...")
        else:
            self.simulator.running = False
            self.start_stop_button.config(text="Start")
            # Cancel scheduled GUI update if any
            if self._animation_job:
                self.root.after_cancel(self._animation_job)
                self._animation_job = None
            # Thread will exit on its own as self.simulator.running is False
            self.status_var.set("Status: Paused")


    def _reset_sim(self):
        """Reset the simulation."""
        if self.simulator.running:
            self._toggle_simulation() # Stop simulation first
            time.sleep(0.1) # Give thread time to stop

        self.simulator.reset_simulation()
        self._update_gui() # Update display with reset state
        self.status_var.set("Status: Reset | Steps: 0 | Particles: 0")


    def _on_closing(self):
        """Handle window close event."""
        print("Closing simulation...")
        self.simulator.running = False # Signal thread to stop
        if hasattr(self, 'sim_thread') and self.sim_thread.is_alive():
            print("Waiting for simulation thread to finish...")
            # self.sim_thread.join(timeout=0.5) # Wait briefly for thread
        print("Destroying window.")
        plt.close(self.fig) # Close matplotlib figure
        self.root.quit() # Quit Tkinter main loop
        self.root.destroy() # Destroy window


if __name__ == "__main__":
    root = tk.Tk()
    sim_instance = EmergentParticleSimulator(grid_size=128) # Increased grid size
    app = SimulationGUI(root, sim_instance)
    root.geometry("900x750") # Adjust window size
    root.mainloop()