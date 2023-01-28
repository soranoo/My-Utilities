import React from "react";
import { Menu, Popover, Transition } from "@headlessui/react"
import { MagnifyingGlassSolid, BellOutline, Bars3Outline, XMarkOutline } from "@graywolfai/react-heroicons"

function Footer() {
    return (
        <>
            <MagnifyingGlassSolid className="h-5 w-5 text-gray-400" aria-hidden="true" />
            <h1 className="text-3xl font-bold underline text-blue-200">
                Footer
            </h1>
        </>
    );
}

export default Footer;