document.addEventListener('DOMContentLoaded', function() {
  const processSelect = document.getElementById('process-select');
  const dynamicFields = document.getElementById('dynamic-fields');
  const otherProcessField = document.getElementById('other-process-field');
  
  // Process field definitions
  const processFields = {
    coal_mining: [
      { name: 'electricity_usage', label: 'Electricity Usage (kWh)', type: 'number', min: 0 },
      { name: 'fuel_consumption', label: 'Fuel Consumption (liters)', type: 'number', min: 0 },
      { name: 'mining_area', label: 'Mining Area (hectares)', type: 'number', min: 0 }
    ],
    manufacturing: [
      { name: 'electricity_usage', label: 'Electricity Usage (kWh)', type: 'number', min: 0 },
      { name: 'raw_materials', label: 'Raw Materials (tons)', type: 'number', min: 0 },
      { name: 'waste_produced', label: 'Waste Produced (tons)', type: 'number', min: 0 }
    ],
    transportation: [
      { name: 'fuel_type', label: 'Fuel Type', type: 'select', options: ['Diesel', 'Gasoline', 'Electric', 'Hybrid'] },
      { name: 'distance', label: 'Distance Traveled (km)', type: 'number', min: 0 },
      { name: 'vehicle_count', label: 'Number of Vehicles', type: 'number', min: 1 }
    ],
    waste_management: [
      { name: 'waste_volume', label: 'Waste Volume (tons)', type: 'number', min: 0 },
      { name: 'recycling_percentage', label: 'Recycling Percentage', type: 'range', min: 0, max: 100 },
      { name: 'landfill_area', label: 'Landfill Area (hectares)', type: 'number', min: 0 }
    ]
  };
  
  // Handle process selection change
  processSelect.addEventListener('change', function() {
    const selectedProcess = this.value;
    
    // Clear previous fields
    dynamicFields.innerHTML = '';
    dynamicFields.classList.add('hidden');
    otherProcessField.classList.add('hidden');
    
    if (selectedProcess === 'other') {
      // Show the other process description field
      otherProcessField.classList.remove('hidden');
      return;
    }
    
    if (selectedProcess && processFields[selectedProcess]) {
      // Create fields for the selected process
      processFields[selectedProcess].forEach(field => {
        const fieldContainer = document.createElement('div');
        fieldContainer.className = 'field-container';
        
        const label = document.createElement('label');
        label.textContent = field.label;
        fieldContainer.appendChild(label);
        
        let input;
        
        if (field.type === 'select') {
          input = document.createElement('select');
          input.name = field.name;
          input.required = true;
          
          // Add empty option
          const emptyOption = document.createElement('option');
          emptyOption.value = '';
          emptyOption.textContent = 'Select ' + field.label;
          input.appendChild(emptyOption);
          
          // Add options
          field.options.forEach(optionText => {
            const option = document.createElement('option');
            option.value = optionText.toLowerCase();
            option.textContent = optionText;
            input.appendChild(option);
          });
        } else {
          input = document.createElement('input');
          input.type = field.type;
          input.name = field.name;
          input.required = true;
          
          if (field.min !== undefined) input.min = field.min;
          if (field.max !== undefined) input.max = field.max;
          
          if (field.type === 'range') {
            const valueDisplay = document.createElement('span');
            valueDisplay.className = 'range-value';
            valueDisplay.textContent = '50%'; // Default value
            
            input.value = 50; // Default value
            input.addEventListener('input', function() {
              valueDisplay.textContent = this.value + '%';
            });
            
            fieldContainer.appendChild(input);
            fieldContainer.appendChild(valueDisplay);
          } else {
            fieldContainer.appendChild(input);
          }
        }
        
        if (field.type !== 'range') {
          fieldContainer.appendChild(input);
        }
        
        dynamicFields.appendChild(fieldContainer);
      });
      
      dynamicFields.classList.remove('hidden');
    }
  });
});