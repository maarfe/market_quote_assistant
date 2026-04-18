"""Application entry point for the Market Quote Assistant project."""

import json

from app.output import CliRenderer, JsonRenderer, SummaryRenderer
from app.services import ApplicationService, CliConfigService, ResultExportService
from app.shared import (
    InvalidDeliveryFeeConfigError,
    InvalidMarketSourceConfigError,
    InvalidShoppingListError,
    UnsupportedUnitError,
)


def main() -> None:
    """Run the Market Quote Assistant application."""
    cli_config_service = CliConfigService()
    application_service = ApplicationService()
    cli_renderer = CliRenderer()
    json_renderer = JsonRenderer()
    summary_renderer = SummaryRenderer()
    result_export_service = ResultExportService()

    try:
        cli_config = cli_config_service.parse_args()

        comparison_result = application_service.run(
            shopping_list_path=cli_config.shopping_list_path,
            delivery_fees_path=cli_config.delivery_fees_path,
            market_sources_path=cli_config.market_sources_path,
            delivery_address_path=cli_config.delivery_address_path,
        )

        json_output = None
        if cli_config.output_mode in {"json", "both"} or cli_config.export_json_path:
            json_output = json_renderer.render_comparison_result(comparison_result)

        if cli_config.output_mode == "summary":
            summary_output = summary_renderer.render_comparison_result(
                comparison_result
            )
            print(summary_output)

        else:
            if cli_config.output_mode in {"cli", "both"}:
                cli_output = cli_renderer.render_comparison_result(comparison_result)
                print(cli_output)

            if cli_config.output_mode in {"json", "both"}:
                if cli_config.output_mode == "both":
                    print()
                    print("JSON preview:")

                print(json.dumps(json_output, indent=2, ensure_ascii=False))

        if cli_config.export_json_path:
            exported_path = result_export_service.export_json(
                file_path=cli_config.export_json_path,
                payload=json_output,
            )
            print(f"JSON result exported to: {exported_path}")

    except FileNotFoundError as error:
        print(f"Error: required file not found: {error.filename}")
        raise SystemExit(1) from error

    except InvalidShoppingListError as error:
        print(f"Error: invalid shopping list: {error}")
        raise SystemExit(1) from error

    except InvalidDeliveryFeeConfigError as error:
        print(f"Error: invalid delivery fee configuration: {error}")
        raise SystemExit(1) from error

    except InvalidMarketSourceConfigError as error:
        print(f"Error: invalid market source configuration: {error}")
        raise SystemExit(1) from error

    except UnsupportedUnitError as error:
        print(f"Error: unsupported unit detected: {error}")
        raise SystemExit(1) from error

    except ValueError as error:
        print(f"Error: invalid input or configuration: {error}")
        raise SystemExit(1) from error

    except Exception as error:
        print(f"Unexpected error: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()