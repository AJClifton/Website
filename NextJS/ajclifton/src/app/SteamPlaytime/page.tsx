export default function Main() {
    return <ul>{[...Array(10)].map((element, index) => {
        let a = index.toString();
        return (<Item value={a}/>);
    })}
    </ul>
}

function Item({value}: {value: string}) {
    return <li key={value}>{value}</li>
}

function ListText({value}: {value: string}) {
    return <p>{value}</p>
}