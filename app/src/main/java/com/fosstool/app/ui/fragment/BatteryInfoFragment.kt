package com.fosstool.app.ui.fragment

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import com.fosstool.app.R

class BatteryInfoFragment : Fragment() {
    private lateinit var batteryInfoText: TextView
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent == null || context == null) return
            updateBatteryInfo(intent)
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_battery_info, container, false)
        batteryInfoText = view.findViewById(R.id.battery_info_text)
        return view
    }

    override fun onResume() {
        super.onResume()
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_BATTERY_CHANGED)
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
                addAction("android.intent.action.ADDITIONAL_BATTERY_CHANGED")
            }
        }
        ContextCompat.registerReceiver(
            requireContext(), batteryReceiver, filter, ContextCompat.RECEIVER_NOT_EXPORTED
        )
    }

    override fun onPause() {
        super.onPause()
        requireContext().unregisterReceiver(batteryReceiver)
    }

    private fun updateBatteryInfo(intent: Intent) {
        val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
        val voltage = intent.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1)
        val temperature = intent.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1)
        val status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
        val health = intent.getIntExtra(BatteryManager.EXTRA_HEALTH, -1)
        val technology = intent.getStringExtra(BatteryManager.EXTRA_TECHNOLOGY)
        val plugged = intent.getIntExtra(BatteryManager.EXTRA_PLUGGED, -1)

        val batteryPct = if (level >= 0 && scale > 0) (level.toFloat() / scale.toFloat() * 100).toInt() else -1
        val tempC = if (temperature >= 0) temperature.toFloat() / 10f else -1f
        val voltMV = if (voltage >= 0) voltage else -1

        val unknown = getString(R.string.battery_status_unknown)
        val statusText = getString(when (status) {
            BatteryManager.BATTERY_STATUS_CHARGING -> R.string.battery_status_charging
            BatteryManager.BATTERY_STATUS_DISCHARGING -> R.string.battery_status_discharging
            BatteryManager.BATTERY_STATUS_FULL -> R.string.battery_status_full
            BatteryManager.BATTERY_STATUS_NOT_CHARGING -> R.string.battery_status_not_charging
            else -> R.string.battery_status_unknown
        })
        val healthText = getString(when (health) {
            BatteryManager.BATTERY_HEALTH_GOOD -> R.string.battery_health_good
            BatteryManager.BATTERY_HEALTH_OVERHEAT -> R.string.battery_health_overheat
            BatteryManager.BATTERY_HEALTH_DEAD -> R.string.battery_health_dead
            BatteryManager.BATTERY_HEALTH_OVER_VOLTAGE -> R.string.battery_health_overvoltage
            BatteryManager.BATTERY_HEALTH_UNSPECIFIED_FAILURE -> R.string.battery_health_failure
            BatteryManager.BATTERY_HEALTH_COLD -> R.string.battery_health_cold
            else -> R.string.battery_status_unknown
        })
        val plugText = when (plugged) {
            BatteryManager.BATTERY_PLUGGED_AC -> getString(R.string.battery_plug_ac)
            BatteryManager.BATTERY_PLUGGED_USB -> "USB"
            BatteryManager.BATTERY_PLUGGED_WIRELESS -> getString(R.string.battery_plug_wireless)
            0 -> getString(R.string.battery_unplugged)
            else -> unknown
        }
        fun row(label: Int, value: String) = getString(R.string.battery_info_row, getString(label), value)
        batteryInfoText.text = listOf(
            row(R.string.battery_level_label, if (batteryPct >= 0) "$batteryPct%" else unknown),
            row(R.string.battery_voltage, if (voltMV >= 0) "$voltMV mV" else unknown),
            row(R.string.battery_temperature, if (temperature >= 0) "$tempC °C" else unknown),
            row(R.string.battery_status_label, statusText),
            row(R.string.battery_health_label, healthText),
            row(R.string.battery_chemistry_label, technology?.takeIf { it.isNotBlank() } ?: unknown),
            row(R.string.battery_charger_type, plugText)
        ).joinToString("\n")
    }
}
