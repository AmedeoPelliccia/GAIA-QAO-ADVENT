# quantum_mdo/models/weight_balance_model.py
import json

class EnhancedWeightAndBalanceModel:
    """
    An enhanced model to manage and analyze aircraft weight and balance data,
    aligning with the GAIA-QAO MDO framework.

    This model is designed to be populated directly from the digital thread,
    specifically from the data defined in the master STEP AP242 file.
    It includes data integrity checks and a more detailed system breakdown as
    per the digital thread architecture documentation.
    Version: 1.0 (as per documentation)
    """

    def __init__(self, step_data):
        """
        Initializes the model with detailed weight and balance properties.

        Args:
            step_data (dict): A dictionary containing weight and balance properties.
        """
        self.version = step_data.get('version', 'N/A')
        # --- Basic Weights (from #4400, #4410) ---
        self.oew = step_data.get('operational_empty_weight_kg')
        self.mtow = step_data.get('maximum_takeoff_weight_kg')

        # --- System Weights (from #4420, #4430, #4440) ---
        self.system_weights_kg = {
            'structure': step_data.get('structure_weight_kg'),
            'powerplant': step_data.get('powerplant_weight_kg'),
            # The total weight is still sourced from the STEP file
            'quantum_systems_total': step_data.get('quantum_systems_weight_kg')
        }

        # --- Enhanced Quantum System Breakdown (from documentation) ---
        self.quantum_systems_breakdown_kg = step_data.get('quantum_systems_breakdown_kg', {})

        # --- Center of Gravity Locations (from #4450, #4460) ---
        # Format: [X, Y, Z] in mm
        self.cg_locations_mm = {
            'empty': step_data.get('empty_cg_location_mm'),
            'loaded_mtow': step_data.get('loaded_cg_location_mm')
        }
        
        print("EnhancedWeightAndBalanceModel initialized successfully.")
        
        # --- Data Integrity Feature: OEW Validation ---
        self.verify_oew()


    def verify_oew(self, tolerance_kg=100.0):
        """
        Validates that the sum of major system weights is consistent with the OEW.
        This is a data integrity check as specified in the MDO framework.
        """
        # Sum of all explicitly defined system weights
        itemized_weight = sum(self.system_weights_kg.values())
        
        # OEW must be greater than the sum of its parts
        if self.oew < itemized_weight:
             raise ValueError(
                f"OEW validation failed: OEW ({self.oew} kg) is less than the "
                f"sum of itemized systems ({itemized_weight} kg)."
            )
            
        unitemized_weight = self.oew - itemized_weight
        print(f"OEW consistency check passed. Unitemized mass (wiring, etc.): {unitemized_weight:.1f} kg.")
        
        # Check quantum systems breakdown consistency
        if self.quantum_systems_breakdown_kg:
            breakdown_sum = sum(self.quantum_systems_breakdown_kg.values())
            total_quantum_weight = self.system_weights_kg.get('quantum_systems_total', 0)
            if abs(breakdown_sum - total_quantum_weight) > 1: # Small tolerance for float precision
                 raise ValueError(
                    f"Quantum system weight validation failed: Breakdown sum ({breakdown_sum} kg) "
                    f"does not match total ({total_quantum_weight} kg)."
                )
        return True


    def calculate_payload(self) -> float:
        """
        Calculates the maximum payload capacity. Payload = MTOW - OEW.

        Returns:
            float: Maximum payload in kilograms.
        """
        if self.mtow is not None and self.oew is not None:
            return self.mtow - self.oew
        return 0.0

    def get_cg_envelope_summary(self) -> str:
        """
        Provides a summary of the Center of Gravity shift from empty to loaded.

        Returns:
            str: A formatted string describing the CG shift.
        """
        empty_cg = self.cg_locations_mm.get('empty', [0, 0, 0])
        loaded_cg = self.cg_locations_mm.get('loaded_mtow', [0, 0, 0])

        x_shift = loaded_cg[0] - empty_cg[0]
        z_shift = loaded_cg[2] - empty_cg[2]

        summary = (
            f"CG Shift from OEW to MTOW:\n"
            f"  - Longitudinal (X-axis): {x_shift:.2f} mm\n"
            f"  - Vertical (Z-axis):     {z_shift:.2f} mm"
        )
        return summary

    def generate_enhanced_report(self):
        """
        Prints a full, enhanced weight and balance report to the console,
        including a detailed breakdown of quantum systems.
        """
        payload = self.calculate_payload()
        unitemized_weight = self.oew - sum(self.system_weights_kg.values())

        print("\n" + "="*60)
        print("    ENHANCED AIRCRAFT WEIGHT & BALANCE REPORT - BWBQ100")
        print(f"                  (Model Version: {self.version})")
        print("="*60)
        print(f"  Operational Empty Weight (OEW): {self.oew:,.1f} kg")
        print(f"  Maximum Takeoff Weight (MTOW):  {self.mtow:,.1f} kg")
        print("-" * 60)
        print(f"  Calculated Max Payload:         {payload:,.1f} kg")
        print("-" * 60)
        print("  System Weight Breakdown:")
        for system, weight in self.system_weights_kg.items():
            print(f"    - {system.replace('_', ' ').capitalize():<25}: {weight:,.1f} kg")
        
        if self.quantum_systems_breakdown_kg:
            print("      Quantum Systems Detailed Breakdown:")
            for system, weight in self.quantum_systems_breakdown_kg.items():
                print(f"        - {system:<22}: {weight:,.1f} kg")

        print(f"    - Unitemized Systems/Equip.:  {unitemized_weight:,.1f} kg")
        print("-" * 60)
        print("  Center of Gravity (CG) Locations (X, Y, Z) in mm:")
        print(f"    - Empty CG:  {self.cg_locations_mm['empty']}")
        print(f"    - MTOW CG:   {self.cg_locations_mm['loaded_mtow']}")
        print("\n" + self.get_cg_envelope_summary())
        print("="*60)

def load_data_from_step_file_stub():
    """
    Stub function to simulate reading data from the STEP file via a parser.
    This now includes a more detailed data structure as specified in the
    digital thread documentation.
    """
    step_file_data = {
        'version': '1.0',
        # Data from #4402
        'operational_empty_weight_kg': 60000.0,
        # Data from #4411
        'maximum_takeoff_weight_kg': 85000.0,
        # Data from #4421
        'structure_weight_kg': 28500.0,
        # Data from #4431
        'powerplant_weight_kg': 14450.0,
        # Data from #4441
        'quantum_systems_weight_kg': 3200.0,
        # Data from #4451
        'empty_cg_location_mm': [21500.0, 0.0, 2300.0],
        # Data from #4461
        'loaded_cg_location_mm': [21460.0, 0.0, 2260.0],
        # Enhanced data - breakdown of quantum systems
        'quantum_systems_breakdown_kg': {
            'QPU (Processing Unit)': 1500.0,
            'QNS (Navigation System)': 700.0,
            'QSM (Structural Monitoring)': 600.0,
            'QKD (Key Distribution)': 400.0,
        }
    }
    print("Data stub loaded, simulating read from STEP file via parser.")
    return step_file_data

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Load data from the master engineering file (simulated via stub)
    wb_data = load_data_from_step_file_stub()

    # 2. Instantiate the enhanced analysis model
    try:
        bwb_q100_model = EnhancedWeightAndBalanceModel(wb_data)
        # 3. Generate and print the enhanced report
        bwb_q100_model.generate_enhanced_report()
    except ValueError as e:
        print(f"\nERROR: Model instantiation failed due to a data integrity issue.")
        print(f"DETAILS: {e}")
