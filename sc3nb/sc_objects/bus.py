"""Python representation of the scsynth Bus."""

from collections.abc import Iterable
from enum import Enum, unique
from typing import TYPE_CHECKING, Optional, Sequence, Union

import sc3nb

if TYPE_CHECKING:
    from sc3nb.sc_objects.server import SCServer


@unique
class ControlBusCommand(str, Enum):
    """OSC Commands for Control Buses"""

    FILL = "/c_fill"
    SET = "/c_set"
    SETN = "/c_setn"
    GET = "/c_get"
    GETN = "/c_getn"


@unique
class BusRate(str, Enum):
    """Calculation rate of Buses"""

    AUDIO = "audio"
    CONTROL = "control"


class Bus:
    """Represenation of a Control or Audio Bus on the SuperCollider Server"""

    def __init__(
        self,
        rate: Union[BusRate, str],
        num_channels: int = 1,
        index: Optional[int] = None,
        server: Optional["SCServer"] = None,
    ) -> None:
        self._server = server or sc3nb.SC.get_default().server
        self._num_channels = num_channels
        self._rate = rate
        if index is None:
            if self._rate is BusRate.AUDIO:
                self._bus_idxs = self._server.allocate_audio_bus_idx(self._num_channels)
            else:
                self._bus_idxs = self._server.allocate_control_bus_idx(
                    self._num_channels
                )
        else:
            self._bus_idxs = list(range(index, index + num_channels))
        if num_channels > 1:
            assert (
                len(self._bus_idxs) == num_channels
            ), "Not enough idxes for number of channels"

    @property
    def rate(self) -> Union[BusRate, str]:
        """The bus calculation rate.

        Returns
        -------
        BusRate
            the rate of this bus
        """
        return self._rate

    @property
    def num_channels(self) -> int:
        """The number of buses.

        Returns
        -------
        int
            number of buses allocated
        """
        return self._num_channels

    @property
    def idxs(self) -> Sequence[int]:
        """The bus index(s).

        Returns
        -------
        int
            first bus index
        """
        return self._bus_idxs

    def is_audio_bus(self) -> bool:
        """Rate check

        Returns
        -------
        bool
            True if this is a audio bus
        """
        return self._rate is BusRate.AUDIO

    def is_control_bus(self) -> bool:
        """Rate check

        Returns
        -------
        bool
            True if this is a control bus
        """
        return self._rate is BusRate.CONTROL

    def set(self, *values: Sequence[Union[int, float]]) -> None:
        """Set ranges of bus values.

        Parameters
        ----------
        values : sequence of int or float
            Values that should be set

        Raises
        ------
        RuntimeError
            If trying to setn an Audio Bus
        """
        if self._rate is BusRate.AUDIO:
            raise RuntimeError("Can't setn Audio Buses")
        if self._num_channels > 1:
            if len(values) != self._num_channels:
                raise ValueError(
                    f"lenght of values must fit num channels ({self._num_channels})"
                )
            self._server.msg(
                ControlBusCommand.SETN, [self._bus_idxs[0], self._num_channels, *values]
            )
        else:
            self._server.msg(ControlBusCommand.SET, [self._bus_idxs[0], *values])

    def fill(self, value: Union[int, float]) -> None:
        """Fill bus(es) to one value.

        Parameters
        ----------
        value : Union[int, float]
            value for the buses

        Raises
        ------
        RuntimeError
            If fill is used on a Audio Bus
        """
        if self._rate is BusRate.AUDIO:
            raise RuntimeError("Can't fill Audio Buses")
        self._server.msg(
            ControlBusCommand.FILL, [self._bus_idxs[0], self._num_channels, value]
        )

    def get(self) -> Union[Union[int, float], Sequence[Union[int, float]]]:
        """Get bus value(s).

        Returns
        -------
        bus value or sequence of bus values
            The current value of this bus
            Multiple values if this bus has num_channels > 1

        Raises
        ------
        RuntimeError
            If get is used on an Audio Bus
        """
        if self._rate is BusRate.AUDIO:
            raise RuntimeError("Can't get Audio Buses")
        if self._num_channels > 1:
            msg_args = [self._bus_idxs[0], self._num_channels]
            response = self._server.msg(ControlBusCommand.GETN, msg_args)
            if isinstance(response, Iterable):
                _, _, *values = response
                return values
            raise RuntimeError(f"Failed to get right response, got {response}")
        else:
            response = self._server.msg(ControlBusCommand.GET, [self._bus_idxs[0]])
            if isinstance(response, Iterable):
                _, value = response
                return value
            raise RuntimeError(f"Failed to get right response, got {response}")

    def free(self, clear: bool = True) -> None:
        """Mark this Buses ids as free again

        Parameters
        ----------
        clear : bool, optional
            Reset bus value(s) to 0, by default True
        """
        if self._rate is BusRate.AUDIO:
            self._bus_idxs = self._server.audio_bus_id_allocator.free_ids(
                self._bus_idxs
            )
        else:
            if clear:
                self.fill(0)
            self._bus_idxs = self._server.control_bus_id_allocator.free_ids(
                self._bus_idxs
            )

    def __del__(self) -> None:
        if self._bus_idxs:
            self.free()

    def __repr__(self) -> str:
        return f"Bus({self.rate}, ids={self._bus_idxs})"
